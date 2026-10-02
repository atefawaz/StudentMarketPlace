"""
Race-condition tests for PATCH /items/{id} ("mark as sold").

A check-then-update implementation (SELECT is_sold, then UPDATE) lets several
concurrent requests all read "not sold yet" and all report success. The fix is
a single conditional UPDATE whose rowcount decides the winner, so exactly one
request may succeed and every other one must get a 409.
"""

import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

import pytest
from fastapi import FastAPI, HTTPException
from fastapi.testclient import TestClient

from database import get_db

CONCURRENT_REQUESTS = 20
ROUNDS = 10

NEW_ITEM = {
    "title": "Race Condition Bike",
    "description": "Everybody wants it",
    "price": 120.0,
    "category": "Sports",
}


# ---------------------------------------------------------------------------
# Helpers and fixtures
# ---------------------------------------------------------------------------


def fire_concurrently(send, n=CONCURRENT_REQUESTS):
    """
    Call send() from n threads released at the same instant by a barrier,
    and return the n responses.
    """
    barrier = Barrier(n)

    def worker(_):
        barrier.wait()
        return send()

    with ThreadPoolExecutor(max_workers=n) as pool:
        return list(pool.map(worker, range(n)))


def status_counts(responses):
    return Counter(r.status_code for r in responses)


def is_sold_in_db(item_id):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT is_sold FROM items WHERE id = %s", (item_id,))
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def set_sold_in_db(item_id, value):
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute("UPDATE items SET is_sold = %s WHERE id = %s", (value, item_id))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


@pytest.fixture
def owner(make_seller):
    return make_seller("race_owner")


def create_item(client, headers):
    response = client.post("/items", json=NEW_ITEM, headers=headers)
    assert response.status_code == 201, response.text
    return response.json()


# ---------------------------------------------------------------------------
# Harness sanity check: the test setup must be able to expose the bug
# ---------------------------------------------------------------------------


def test_harness_detects_check_then_update_race(client, owner):
    """
    A check-then-update handler (the pre-fix pattern) must let more than one
    of the 20 concurrent requests through. If this ever fails, the harness is
    too weak to prove anything and the tests below are meaningless.
    """
    naive = FastAPI()

    @naive.patch("/items/{item_id}")
    def naive_mark_sold(item_id: int):
        conn = get_db()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT is_sold FROM items WHERE id = %s", (item_id,))
            if cursor.fetchone()["is_sold"]:
                raise HTTPException(status_code=409, detail="Item is already sold")
            time.sleep(0.05)  # widen the check -> update window
            cursor.execute("UPDATE items SET is_sold = 1 WHERE id = %s", (item_id,))
            conn.commit()
            return {"id": item_id, "is_sold": True}
        finally:
            cursor.close()
            conn.close()

    item = create_item(client, owner[1])
    naive_client = TestClient(naive)

    responses = fire_concurrently(
        lambda: naive_client.patch(f"/items/{item['id']}", json={"is_sold": True})
    )

    successes = status_counts(responses)[200]
    assert successes > 1, f"expected the naive handler to race, got {successes} success"


# ---------------------------------------------------------------------------
# PATCH /items/{id}: exactly one winner
# ---------------------------------------------------------------------------


def test_concurrent_mark_as_sold_has_exactly_one_winner(client, owner):
    _, headers = owner
    item = create_item(client, headers)

    responses = fire_concurrently(
        lambda: client.patch(f"/items/{item['id']}", json={"is_sold": True}, headers=headers)
    )

    counts = status_counts(responses)
    assert counts[200] == 1, counts
    assert counts[409] == CONCURRENT_REQUESTS - 1, counts
    assert set(counts) == {200, 409}, counts  # no 5xx from lock contention
    assert is_sold_in_db(item["id"]) == 1


def test_mark_as_sold_race_is_stable_over_repeated_runs(client, owner):
    """The same 20-concurrent script, 10 times in a row, on a fresh item each time."""
    _, headers = owner

    for round_number in range(1, ROUNDS + 1):
        item = create_item(client, headers)

        responses = fire_concurrently(
            lambda: client.patch(
                f"/items/{item['id']}", json={"is_sold": True}, headers=headers
            )
        )

        counts = status_counts(responses)
        assert counts[200] == 1, f"round {round_number}: {counts}"
        assert counts[409] == CONCURRENT_REQUESTS - 1, f"round {round_number}: {counts}"
        assert is_sold_in_db(item["id"]) == 1, f"round {round_number}"


def test_losers_get_a_clear_409(client, owner):
    _, headers = owner
    item = create_item(client, headers)

    responses = fire_concurrently(
        lambda: client.patch(f"/items/{item['id']}", json={"is_sold": True}, headers=headers)
    )

    losers = [r for r in responses if r.status_code != 200]
    assert len(losers) == CONCURRENT_REQUESTS - 1
    assert all(r.json() == {"detail": "Item is already sold"} for r in losers)


def test_winner_response_is_the_updated_item(client, owner):
    _, headers = owner
    item = create_item(client, headers)

    responses = fire_concurrently(
        lambda: client.patch(f"/items/{item['id']}", json={"is_sold": True}, headers=headers)
    )

    winners = [r for r in responses if r.status_code == 200]
    assert len(winners) == 1
    assert winners[0].json() == {**item, "is_sold": True}


def test_concurrent_requests_on_an_already_sold_item_all_conflict(client, owner):
    _, headers = owner
    item = create_item(client, headers)
    assert client.patch(
        f"/items/{item['id']}", json={"is_sold": True}, headers=headers
    ).status_code == 200

    responses = fire_concurrently(
        lambda: client.patch(f"/items/{item['id']}", json={"is_sold": True}, headers=headers)
    )

    assert status_counts(responses) == {409: CONCURRENT_REQUESTS}
    assert is_sold_in_db(item["id"]) == 1


def test_concurrent_mark_as_available_has_exactly_one_winner(client, owner):
    """The conditional UPDATE guards the reverse transition too."""
    _, headers = owner
    item = create_item(client, headers)
    set_sold_in_db(item["id"], 1)

    responses = fire_concurrently(
        lambda: client.patch(f"/items/{item['id']}", json={"is_sold": False}, headers=headers)
    )

    counts = status_counts(responses)
    assert counts[200] == 1, counts
    assert counts[409] == CONCURRENT_REQUESTS - 1, counts
    assert is_sold_in_db(item["id"]) == 0


def test_race_on_one_item_does_not_leak_to_other_items(client, owner):
    _, headers = owner
    contested = create_item(client, headers)
    bystander = create_item(client, headers)

    responses = fire_concurrently(
        lambda: client.patch(
            f"/items/{contested['id']}", json={"is_sold": True}, headers=headers
        )
    )

    assert status_counts(responses)[200] == 1
    assert is_sold_in_db(contested["id"]) == 1
    assert is_sold_in_db(bystander["id"]) == 0


def test_concurrent_races_on_different_items_each_have_one_winner(client, owner):
    _, headers = owner
    items = [create_item(client, headers) for _ in range(3)]
    per_item = CONCURRENT_REQUESTS // len(items)

    barrier = Barrier(per_item * len(items))

    def worker(item_id):
        barrier.wait()
        return item_id, client.patch(
            f"/items/{item_id}", json={"is_sold": True}, headers=headers
        )

    ids = [item["id"] for item in items for _ in range(per_item)]
    with ThreadPoolExecutor(max_workers=len(ids)) as pool:
        results = list(pool.map(worker, ids))

    for item in items:
        counts = status_counts([r for item_id, r in results if item_id == item["id"]])
        assert counts[200] == 1, f"item {item['id']}: {counts}"
        assert counts[409] == per_item - 1, f"item {item['id']}: {counts}"
        assert is_sold_in_db(item["id"]) == 1
