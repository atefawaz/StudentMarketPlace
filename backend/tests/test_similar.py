"""
Tests for GET /items/{id}/similar.

Returns up to 5 items sharing the item's category, newest first (ties broken
by id descending), excluding the item itself. 404 if the item does not exist.
"""

import pytest

import database


def insert_item(title, category, created_at, seller_id=1):
    """Insert an item with an explicit created_at (TIMESTAMP has 1s resolution)."""
    db = database.get_db()
    cur = db.cursor()
    cur.execute(
        """
        INSERT INTO items (title, price, category, seller_name, seller_id, created_at)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (title, 10.0, category, "Seller", seller_id, created_at),
    )
    item_id = cur.lastrowid
    db.commit()
    cur.close()
    db.close()
    return item_id


def similar(client, item_id):
    return client.get(f"/items/{item_id}/similar")


def ids(response):
    assert response.status_code == 200, response.text
    return [item["id"] for item in response.json()]


def test_unknown_item_returns_404(client):
    response = similar(client, 999999)
    assert response.status_code == 404
    assert response.json()["detail"] == "Item not found"


def test_non_integer_id_is_rejected(client):
    assert similar(client, "abc").status_code == 400


def test_item_alone_in_category_returns_empty_list(client):
    only = insert_item("Lonely", "Solo", "2026-01-01 10:00:00")
    response = similar(client, only)
    assert response.status_code == 200
    assert response.json() == []


def test_excludes_the_item_itself(client):
    a = insert_item("A", "Gadgets", "2026-01-01 10:00:00")
    b = insert_item("B", "Gadgets", "2026-01-02 10:00:00")
    assert ids(similar(client, a)) == [b]
    assert ids(similar(client, b)) == [a]


def test_only_returns_same_category(client):
    a = insert_item("A", "Gadgets", "2026-01-01 10:00:00")
    b = insert_item("B", "Gadgets", "2026-01-02 10:00:00")
    insert_item("Other", "Toys", "2026-01-03 10:00:00")
    assert ids(similar(client, a)) == [b]


def test_ordered_newest_first(client):
    base = insert_item("Base", "Gadgets", "2026-01-01 10:00:00")
    old = insert_item("Old", "Gadgets", "2026-01-02 10:00:00")
    new = insert_item("New", "Gadgets", "2026-01-04 10:00:00")
    mid = insert_item("Mid", "Gadgets", "2026-01-03 10:00:00")
    assert ids(similar(client, base)) == [new, mid, old]


def test_ties_on_created_at_break_by_id_descending(client):
    base = insert_item("Base", "Gadgets", "2026-01-01 10:00:00")
    first = insert_item("First", "Gadgets", "2026-02-01 10:00:00")
    second = insert_item("Second", "Gadgets", "2026-02-01 10:00:00")
    third = insert_item("Third", "Gadgets", "2026-02-01 10:00:00")
    assert ids(similar(client, base)) == [third, second, first]


def test_limited_to_five_newest(client):
    base = insert_item("Base", "Gadgets", "2026-01-01 10:00:00")
    others = [
        insert_item(f"Item {n}", "Gadgets", f"2026-01-{n + 1:02d} 10:00:00")
        for n in range(1, 9)
    ]
    # the five most recent of the eight, newest first
    assert ids(similar(client, base)) == list(reversed(others))[:5]


def test_exactly_five_others_returns_all_five(client):
    base = insert_item("Base", "Gadgets", "2026-01-01 10:00:00")
    others = [
        insert_item(f"Item {n}", "Gadgets", f"2026-01-{n + 1:02d} 10:00:00")
        for n in range(1, 6)
    ]
    assert ids(similar(client, base)) == list(reversed(others))


@pytest.mark.parametrize("category", ["Men's Wear", 'Say "hi"', "100% Cotton", "a_b", "Back\\slash"])
def test_categories_with_special_characters(client, category):
    a = insert_item("A", category, "2026-01-01 10:00:00")
    b = insert_item("B", category, "2026-01-02 10:00:00")
    insert_item("Decoy", "Men", "2026-01-03 10:00:00")
    insert_item("Decoy2", "aXb", "2026-01-03 10:00:00")
    assert ids(similar(client, a)) == [b]


def test_response_matches_item_schema(client):
    a = insert_item("A", "Gadgets", "2026-01-01 10:00:00")
    insert_item("B", "Gadgets", "2026-01-02 10:00:00")
    (item,) = similar(client, a).json()
    assert set(item) == {
        "id", "title", "description", "price", "category", "image_url",
        "seller_name", "seller_id", "created_at", "is_sold",
    }
    assert item["is_sold"] is False
    assert item["title"] == "B"


def test_does_not_shadow_item_detail(client):
    a = insert_item("A", "Gadgets", "2026-01-01 10:00:00")
    assert client.get(f"/items/{a}").json()["id"] == a
