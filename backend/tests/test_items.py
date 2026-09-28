"""
Tests for the /items endpoints.

Some tests are expected to FAIL because the corresponding features are
not yet implemented — students must make them pass during the challenge week.
"""

import pytest


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


def test_create_item(client):
    """POST /items creates a new item and returns it."""
    payload = {
        "title": "New Headphones",
        "description": "Wireless, noise-cancelling",
        "price": 89.99,
        "category": "Electronics",
        "seller_name": "Dave",
    }
    response = client.post("/items", json=payload)
    assert response.status_code == 201
    item = response.json()
    assert item["title"] == "New Headphones"
    assert item["price"] == 89.99
    assert item["is_sold"] is False
    assert "id" in item


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


def test_mark_as_sold(client):
    """PATCH /items/1 with {"is_sold": true} marks the item as sold.

    TODO: Implement a PATCH /items/{id} endpoint that accepts partial updates.
    """
    response = client.patch("/items/1", json={"is_sold": True})
    assert response.status_code == 200
    item = response.json()
    assert item["is_sold"] is True

    # Verify persistence
    response = client.get("/items/1")
    assert response.json()["is_sold"] is True
