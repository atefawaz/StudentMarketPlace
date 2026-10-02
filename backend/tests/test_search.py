"""
Tests for the `search` query parameter of GET /items.

search matches title OR description, case-insensitively, as a literal
substring (LIKE wildcards are escaped), and combines with `category` / `sort`.
"""

import pytest

SEARCH_ITEMS = [
    # (title, description, price, category)
    ("Calculus Textbook", "Thomas Calculus, 14th edition", 30.0, "Books"),
    ("Desk Lamp", "LED lamp, barely used", 15.0, "Furniture"),
    ("Cotton Hoodie", "Size M, 100% cotton, grey", 25.0, "Clothing"),
    ("Snake_case Poster", "A python poster", 5.0, "Decor"),
    ("Plain Poster", "Snakexcase would match an unescaped underscore", 6.0, "Decor"),
    ("O'Reilly Python Book", None, 40.0, "Books"),
    ("Back\\slash Notes", "Lecture notes", 8.0, "Books"),
    ("Mystery Box", "Contains a LAMP shade", 9.0, "Decor"),
]


@pytest.fixture
def seller_headers(make_seller):
    return make_seller("search_owner")[1]


@pytest.fixture
def catalog(client, seller_headers):
    """Create SEARCH_ITEMS and return {title: item}."""
    created = {}
    for title, description, price, category in SEARCH_ITEMS:
        payload = {"title": title, "price": price, "category": category}
        if description is not None:
            payload["description"] = description
        response = client.post("/items", json=payload, headers=seller_headers)
        assert response.status_code == 201, response.text
        created[title] = response.json()
    return created


def search(client, term, **params):
    return client.get("/items", params={"search": term, **params})


def titles(response):
    assert response.status_code == 200, response.text
    return [item["title"] for item in response.json()]


# ---------------------------------------------------------------------------
# Matching
# ---------------------------------------------------------------------------


def test_search_matches_title(client, catalog):
    assert titles(search(client, "Calculus")) == ["Calculus Textbook"]


def test_search_matches_description(client, catalog):
    assert titles(search(client, "barely used")) == ["Desk Lamp"]


def test_search_matches_title_or_description(client, catalog):
    # "lamp" is in a title ("Desk Lamp") and in a description ("Mystery Box")
    assert sorted(titles(search(client, "lamp"))) == ["Desk Lamp", "Mystery Box"]


def test_search_matches_a_substring_in_the_middle_of_a_word(client, catalog):
    assert titles(search(client, "culus Text")) == ["Calculus Textbook"]


@pytest.mark.parametrize("term", ["calculus", "CALCULUS", "CaLcUlUs"])
def test_search_is_case_insensitive(client, catalog, term):
    assert titles(search(client, term)) == ["Calculus Textbook"]


def test_search_strips_surrounding_whitespace(client, catalog):
    assert titles(search(client, "   Calculus  ")) == ["Calculus Textbook"]


def test_search_keeps_inner_whitespace(client, catalog):
    assert titles(search(client, "Desk Lamp")) == ["Desk Lamp"]
    assert titles(search(client, "DeskLamp")) == []


def test_search_ignores_items_with_null_description(client, catalog):
    # "O'Reilly Python Book" has no description; it must still match on title
    assert titles(search(client, "reilly")) == ["O'Reilly Python Book"]


def test_search_matches_across_the_seed_data(client):
    # seeded in conftest, no catalog fixture
    assert titles(search(client, "laptop")) == ["Test Laptop"]
    assert titles(search(client, "already sold")) == ["Sold Chair"]


def test_search_includes_sold_items(client):
    response = search(client, "chair")

    assert titles(response) == ["Sold Chair"]
    assert response.json()[0]["is_sold"] is True


def test_search_with_no_match_returns_empty_list(client, catalog):
    response = search(client, "zzz-no-such-item")

    assert response.status_code == 200
    assert response.json() == []


# ---------------------------------------------------------------------------
# Empty / missing search is a no-op
# ---------------------------------------------------------------------------


def test_no_search_param_returns_everything(client, catalog):
    assert len(client.get("/items").json()) == len(SEARCH_ITEMS) + 3  # + conftest seed


@pytest.mark.parametrize("term", ["", " ", "     "], ids=["empty", "space", "spaces"])
def test_blank_search_returns_everything(client, catalog, term):
    unfiltered = client.get("/items").json()

    response = search(client, term)

    assert response.status_code == 200
    assert response.json() == unfiltered


# ---------------------------------------------------------------------------
# Response shape
# ---------------------------------------------------------------------------


def test_search_results_are_full_items(client, catalog):
    results = search(client, "Calculus").json()

    assert results == [catalog["Calculus Textbook"]]


def test_search_is_public(client, catalog):
    # no Authorization header anywhere in this file's search calls
    assert search(client, "Calculus").status_code == 200


# ---------------------------------------------------------------------------
# LIKE wildcards and special characters are matched literally
# ---------------------------------------------------------------------------


def test_percent_is_not_a_wildcard(client, catalog):
    # a bare "%" must match only the one description that contains a "%"
    assert titles(search(client, "%")) == ["Cotton Hoodie"]


def test_percent_inside_a_term_is_literal(client, catalog):
    assert titles(search(client, "100%")) == ["Cotton Hoodie"]
    assert titles(search(client, "1%0")) == []  # would match "100" if % were a wildcard


def test_underscore_is_not_a_wildcard(client, catalog):
    # "_" must not match any character, so "Snakexcase" must not be returned
    assert titles(search(client, "snake_case")) == ["Snake_case Poster"]


def test_bare_underscore_matches_only_a_literal_underscore(client, catalog):
    assert titles(search(client, "_")) == ["Snake_case Poster"]


def test_backslash_is_matched_literally(client, catalog):
    assert titles(search(client, "\\")) == ["Back\\slash Notes"]
    assert titles(search(client, "Back\\slash")) == ["Back\\slash Notes"]


def test_apostrophe_is_handled(client, catalog):
    assert titles(search(client, "O'Reilly")) == ["O'Reilly Python Book"]


# ---------------------------------------------------------------------------
# SQL injection attempts are treated as plain text
# ---------------------------------------------------------------------------

INJECTIONS = [
    "' OR '1'='1",
    "' OR 1=1 -- ",
    "%' OR '1'='1' -- ",
    "'; DROP TABLE items; -- ",
    "' UNION SELECT id, password_hash, email, 0, '', '', '', 0, '', 0 FROM sellers -- ",
    "\\' OR 1=1 -- ",
]


@pytest.mark.parametrize("payload", INJECTIONS)
def test_sql_injection_payloads_match_nothing(client, catalog, payload):
    response = search(client, payload)

    assert response.status_code == 200
    assert response.json() == []


def test_sql_injection_does_not_damage_the_data(client, catalog):
    search(client, "'; DROP TABLE items; -- ")

    assert len(client.get("/items").json()) == len(SEARCH_ITEMS) + 3


def test_sql_injection_cannot_leak_other_tables(client, catalog):
    body = search(client, INJECTIONS[4]).text

    assert "$2b$" not in body  # no bcrypt hashes
    assert "@epita.fr" not in body  # no seller emails


# ---------------------------------------------------------------------------
# Length limit
# ---------------------------------------------------------------------------


def test_search_at_max_length_is_accepted(client, catalog):
    response = search(client, "a" * 100)

    assert response.status_code == 200
    assert response.json() == []


def test_search_over_max_length_is_a_validation_error(client, catalog):
    response = search(client, "a" * 101)

    # 400 (not 422) because app.py maps validation errors to 400
    assert response.status_code == 400
    assert response.json()["detail"] == "Validation failed"
    assert "search" in response.json()["errors"]["query"]


# ---------------------------------------------------------------------------
# Combination with category and sort
# ---------------------------------------------------------------------------


def test_search_combines_with_category(client, catalog):
    # "python" appears in a Decor description and in a Books title
    assert sorted(titles(search(client, "python"))) == [
        "O'Reilly Python Book",
        "Snake_case Poster",
    ]
    assert titles(search(client, "python", category="Books")) == ["O'Reilly Python Book"]
    assert titles(search(client, "python", category="Decor")) == ["Snake_case Poster"]


def test_search_and_category_are_anded_not_ored(client, catalog):
    assert titles(search(client, "Calculus", category="Furniture")) == []


def test_search_sorted_by_price(client, catalog):
    ascending = search(client, "poster", sort="price_asc").json()
    descending = search(client, "poster", sort="price_desc").json()

    assert [i["price"] for i in ascending] == [5.0, 6.0]
    assert [i["price"] for i in descending] == [6.0, 5.0]


def test_search_default_order_is_newest_first(client, catalog):
    results = search(client, "poster").json()

    # both created in the same fixture run: later id = newer
    assert [i["id"] for i in results] == sorted((i["id"] for i in results), reverse=True)


def test_search_with_category_and_sort(client, catalog):
    result = search(client, "book", category="Books", sort="price_desc")

    # 40.0, 30.0, then the conftest-seeded "Test Book" at 12.5
    assert titles(result) == ["O'Reilly Python Book", "Calculus Textbook", "Test Book"]
