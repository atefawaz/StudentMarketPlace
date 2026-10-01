"""
Tests for the /items endpoints.

Some tests are expected to FAIL because the corresponding features are
not yet implemented — students must make them pass during the challenge week.
"""

from datetime import datetime, timedelta, timezone

import jwt
import pytest

import auth


# ---------------------------------------------------------------------------
# Tests that SHOULD PASS (features already implemented)
# ---------------------------------------------------------------------------


def test_get_items(client):
    """GET /items returns a JSON list of items."""
    response = client.get("/items")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # seeded in conftest


def test_get_item_by_id(client):
    """GET /items/1 returns the correct item."""
    response = client.get("/items/1")
    assert response.status_code == 200
    item = response.json()
    assert item["id"] == 1
    assert item["title"] == "Test Book"
    assert item["price"] == 12.50


def test_item_not_found(client):
    """GET /items/9999 returns 404."""
    response = client.get("/items/9999")
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Tests that SHOULD FAIL (features NOT yet implemented — TODO for students)
# ---------------------------------------------------------------------------


def test_filter_by_category(client):
    """GET /items?category=Books should return only books.

    TODO: Add a 'category' query parameter to the GET /items endpoint.
    """
    response = client.get("/items?category=Books")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    for item in data:
        assert item["category"] == "Books"


def test_sort_items(client):
    """GET /items?sort=price_asc should return items sorted by price ascending.

    TODO: Add 'sort' query parameter supporting price_asc, price_desc,
          date_asc, date_desc.
    """
    response = client.get("/items?sort=price_asc")
    assert response.status_code == 200
    data = response.json()
    prices = [item["price"] for item in data]
    assert prices == sorted(prices)


# ---------------------------------------------------------------------------
# Helpers and fixtures for the write endpoints (POST / PATCH / DELETE)
# ---------------------------------------------------------------------------

NEW_ITEM = {
    "title": "New Headphones",
    "description": "Wireless, noise-cancelling",
    "price": 89.99,
    "category": "Electronics",
}

ITEM_FIELDS = {
    "id", "title", "description", "price", "category", "image_url",
    "seller_name", "seller_id", "created_at", "is_sold",
}

SEED_ITEM_ID = 1  # "Test Book", owned by a seller nobody can log in as
MISSING_ITEM_ID = 9999


def item_count(client):
    return len(client.get("/items").json())


@pytest.fixture
def owner(make_seller):
    """(seller, headers) of the seller who owns `owned_item`."""
    return make_seller("owner_test")


@pytest.fixture
def intruder(make_seller):
    """(seller, headers) of a second, unrelated seller."""
    return make_seller("intruder_test")


@pytest.fixture
def owned_item(client, owner):
    _, headers = owner
    response = client.post("/items", json=NEW_ITEM, headers=headers)
    assert response.status_code == 201
    return response.json()


def assert_unauthorized(response):
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


# ---------------------------------------------------------------------------
# Authentication: every write endpoint rejects missing / invalid tokens (401)
# ---------------------------------------------------------------------------

WRITE_REQUESTS = {
    "create": lambda c, h: c.post("/items", json=NEW_ITEM, headers=h),
    "update": lambda c, h: c.patch(f"/items/{SEED_ITEM_ID}", json={"is_sold": True}, headers=h),
    "delete": lambda c, h: c.delete(f"/items/{SEED_ITEM_ID}", headers=h),
}


def _signed(key=None, exp_minutes=5, sub="1"):
    claims = {"sub": sub, "exp": datetime.now(timezone.utc) + timedelta(minutes=exp_minutes)}
    return jwt.encode(claims, key or auth.SECRET_KEY, algorithm="HS256")


BAD_AUTH_HEADERS = {
    "no_header": lambda: {},
    "wrong_scheme": lambda: {"Authorization": "Basic dXNlcjpwYXNz"},
    "garbage_token": lambda: {"Authorization": "Bearer not.a.jwt"},
    "wrong_signing_key": lambda: {"Authorization": f"Bearer {_signed(key='x' * 32)}"},
    "expired_token": lambda: {"Authorization": f"Bearer {_signed(exp_minutes=-1)}"},
    "unknown_seller": lambda: {"Authorization": f"Bearer {auth.create_token(999999)}"},
}


@pytest.mark.parametrize("make_headers", BAD_AUTH_HEADERS.values(), ids=BAD_AUTH_HEADERS.keys())
@pytest.mark.parametrize("send", WRITE_REQUESTS.values(), ids=WRITE_REQUESTS.keys())
def test_write_endpoints_reject_bad_credentials(client, send, make_headers):
    before = client.get(f"/items/{SEED_ITEM_ID}").json()
    count = item_count(client)

    assert_unauthorized(send(client, make_headers()))

    # nothing was created, changed or deleted
    assert client.get(f"/items/{SEED_ITEM_ID}").json() == before
    assert item_count(client) == count


def test_read_endpoints_stay_public(client):
    assert client.get("/items").status_code == 200
    assert client.get(f"/items/{SEED_ITEM_ID}").status_code == 200


# ---------------------------------------------------------------------------
# POST /items
# ---------------------------------------------------------------------------


def test_create_item(client, owner):
    _, headers = owner

    response = client.post("/items", json=NEW_ITEM, headers=headers)

    assert response.status_code == 201
    item = response.json()
    assert set(item) == ITEM_FIELDS
    assert item["title"] == "New Headphones"
    assert item["price"] == 89.99
    assert item["is_sold"] is False
    assert isinstance(item["id"], int)


def test_create_item_takes_seller_from_token(client, owner):
    seller, headers = owner

    item = client.post("/items", json=NEW_ITEM, headers=headers).json()

    assert item["seller_id"] == seller["id"]
    assert item["seller_name"] == seller["display_name"]


def test_create_item_is_persisted(client, owner):
    _, headers = owner
    created = client.post("/items", json=NEW_ITEM, headers=headers).json()

    response = client.get(f"/items/{created['id']}")

    assert response.status_code == 200
    assert response.json() == created


def test_create_item_is_listed_for_anonymous_visitors(client, owned_item):
    ids = [item["id"] for item in client.get("/items").json()]
    assert owned_item["id"] in ids


def test_create_item_sets_distinct_owners(client, owner, intruder):
    first = client.post("/items", json=NEW_ITEM, headers=owner[1]).json()
    second = client.post("/items", json=NEW_ITEM, headers=intruder[1]).json()

    assert first["seller_id"] == owner[0]["id"]
    assert second["seller_id"] == intruder[0]["id"]
    assert first["seller_id"] != second["seller_id"]


def test_create_item_optional_fields(client, owner):
    payload = {"title": "Bare minimum", "price": 1, "category": "Books"}

    response = client.post("/items", json=payload, headers=owner[1])

    assert response.status_code == 201
    item = response.json()
    assert item["description"] is None
    assert item["image_url"] is None


def test_create_item_strips_whitespace(client, owner):
    payload = {**NEW_ITEM, "title": "  Padded title  "}

    response = client.post("/items", json=payload, headers=owner[1])

    assert response.status_code == 201
    assert response.json()["title"] == "Padded title"


@pytest.mark.parametrize(
    "extra",
    [
        {"seller_name": "Mallory"},  # no longer client-controlled
        {"seller_id": 1},  # can't be spoofed either
        {"is_sold": True},
    ],
    ids=["seller_name", "seller_id", "is_sold"],
)
def test_create_item_rejects_client_supplied_ownership(client, owner, extra):
    count = item_count(client)

    response = client.post("/items", json={**NEW_ITEM, **extra}, headers=owner[1])

    assert response.status_code == 400
    assert item_count(client) == count


@pytest.mark.parametrize(
    "overrides",
    [
        {"title": ""},
        {"title": "   "},
        {"title": "x" * 201},
        {"price": 0},
        {"price": -5},
        {"price": "free"},
        {"category": ""},
    ],
    ids=[
        "empty_title", "blank_title", "title_too_long",
        "zero_price", "negative_price", "non_numeric_price", "empty_category",
    ],
)
def test_create_item_rejects_invalid_input(client, owner, overrides):
    count = item_count(client)

    response = client.post("/items", json={**NEW_ITEM, **overrides}, headers=owner[1])

    # 400 (not 422) because app.py maps validation errors to 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Validation failed"
    assert item_count(client) == count


@pytest.mark.parametrize("missing", ["title", "price", "category"])
def test_create_item_rejects_missing_required_field(client, owner, missing):
    payload = {k: v for k, v in NEW_ITEM.items() if k != missing}

    response = client.post("/items", json=payload, headers=owner[1])

    assert response.status_code == 400


# ---------------------------------------------------------------------------
# PATCH /items/{id}  (owner only)
# ---------------------------------------------------------------------------


def test_owner_can_mark_item_as_sold(client, owner, owned_item):
    response = client.patch(
        f"/items/{owned_item['id']}", json={"is_sold": True}, headers=owner[1]
    )

    assert response.status_code == 200
    item = response.json()
    assert item["is_sold"] is True
    assert set(item) == ITEM_FIELDS
    # only is_sold changed
    assert item == {**owned_item, "is_sold": True}

    # Verify persistence
    assert client.get(f"/items/{owned_item['id']}").json()["is_sold"] is True


def test_owner_can_mark_item_as_unsold_again(client, owner, owned_item):
    url = f"/items/{owned_item['id']}"
    client.patch(url, json={"is_sold": True}, headers=owner[1])

    response = client.patch(url, json={"is_sold": False}, headers=owner[1])

    assert response.status_code == 200
    assert response.json()["is_sold"] is False
    assert client.get(url).json()["is_sold"] is False


def test_update_does_not_change_ownership(client, owner, owned_item):
    response = client.patch(
        f"/items/{owned_item['id']}", json={"is_sold": True}, headers=owner[1]
    )

    assert response.json()["seller_id"] == owner[0]["id"]
    assert response.json()["seller_name"] == owner[0]["display_name"]


def test_non_owner_cannot_update_item(client, owned_item, intruder):
    url = f"/items/{owned_item['id']}"

    response = client.patch(url, json={"is_sold": True}, headers=intruder[1])

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not own this item"
    assert client.get(url).json() == owned_item  # untouched


def test_cannot_update_item_owned_by_another_seller_from_seed(client, owner):
    response = client.patch(
        f"/items/{SEED_ITEM_ID}", json={"is_sold": True}, headers=owner[1]
    )

    assert response.status_code == 403
    assert client.get(f"/items/{SEED_ITEM_ID}").json()["is_sold"] is False


def test_update_missing_item_returns_404(client, owner):
    response = client.patch(
        f"/items/{MISSING_ITEM_ID}", json={"is_sold": True}, headers=owner[1]
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_update_missing_item_without_token_is_401_not_404(client):
    # Authentication comes first, so anonymous callers can't probe which ids exist
    response = client.patch(f"/items/{MISSING_ITEM_ID}", json={"is_sold": True})

    assert_unauthorized(response)


@pytest.mark.parametrize(
    "body",
    [{}, {"is_sold": "maybe"}, {"is_sold": None}],
    ids=["empty_body", "not_a_bool", "null"],
)
def test_update_rejects_invalid_body(client, owner, owned_item, body):
    response = client.patch(f"/items/{owned_item['id']}", json=body, headers=owner[1])

    assert response.status_code == 400
    assert client.get(f"/items/{owned_item['id']}").json() == owned_item


def test_update_only_touches_is_sold(client, owner, owned_item):
    # ItemSoldUpdate ignores unknown fields, so a title can't be smuggled in
    response = client.patch(
        f"/items/{owned_item['id']}",
        json={"is_sold": True, "title": "Hacked", "price": 0.01},
        headers=owner[1],
    )

    assert response.status_code == 200
    assert response.json() == {**owned_item, "is_sold": True}


# ---------------------------------------------------------------------------
# DELETE /items/{id}  (owner only)
# ---------------------------------------------------------------------------


def test_owner_can_delete_item(client, owner, owned_item):
    url = f"/items/{owned_item['id']}"

    response = client.delete(url, headers=owner[1])

    assert response.status_code == 200
    assert response.json() == {"message": "Item deleted"}
    assert client.get(url).status_code == 404
    assert owned_item["id"] not in [i["id"] for i in client.get("/items").json()]


def test_delete_only_removes_the_targeted_item(client, owner, owned_item):
    other = client.post("/items", json=NEW_ITEM, headers=owner[1]).json()
    count = item_count(client)

    client.delete(f"/items/{owned_item['id']}", headers=owner[1])

    assert item_count(client) == count - 1
    assert client.get(f"/items/{other['id']}").status_code == 200


def test_non_owner_cannot_delete_item(client, owned_item, intruder):
    url = f"/items/{owned_item['id']}"

    response = client.delete(url, headers=intruder[1])

    assert response.status_code == 403
    assert response.json()["detail"] == "You do not own this item"
    assert client.get(url).json() == owned_item  # still there


def test_cannot_delete_seed_item_owned_by_another_seller(client, owner):
    count = item_count(client)

    response = client.delete(f"/items/{SEED_ITEM_ID}", headers=owner[1])

    assert response.status_code == 403
    assert item_count(client) == count


def test_delete_missing_item_returns_404(client, owner):
    response = client.delete(f"/items/{MISSING_ITEM_ID}", headers=owner[1])

    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_delete_missing_item_without_token_is_401_not_404(client):
    assert_unauthorized(client.delete(f"/items/{MISSING_ITEM_ID}"))


def test_delete_twice_returns_404_the_second_time(client, owner, owned_item):
    url = f"/items/{owned_item['id']}"
    assert client.delete(url, headers=owner[1]).status_code == 200

    assert client.delete(url, headers=owner[1]).status_code == 404


def test_deleted_item_cannot_be_updated(client, owner, owned_item):
    url = f"/items/{owned_item['id']}"
    client.delete(url, headers=owner[1])

    assert client.patch(url, json={"is_sold": True}, headers=owner[1]).status_code == 404


@pytest.mark.parametrize("method", ["patch", "delete"])
def test_non_integer_item_id_is_a_validation_error(client, owner, method):
    kwargs = {"json": {"is_sold": True}} if method == "patch" else {}

    response = getattr(client, method)("/items/abc", headers=owner[1], **kwargs)

    assert response.status_code == 400
