"""
Security test suite — automated checks for the CS audit findings.
Run with: pytest tests/test_security.py -v   (server must be running on :5000)
"""
import requests

BASE = "http://localhost:5000"


def _make_item(title="test item", seller="test-seller"):
    r = requests.post(f"{BASE}/items", json={
        "title": title, "description": "x", "price": 1,
        "category": "Books", "seller_name": seller})
    return r.json()["id"] if r.status_code == 201 else None


# C007 — SQL injection (fixed)
def test_sqli_search_no_injection():
    r = requests.get(f"{BASE}/items/search", params={"q": "%' OR '1'='1"})
    assert r.status_code != 500


# C008 — Stored XSS (fixed)
def test_xss_admin_escapes_script():
    _make_item(title="<script>alert('t')</script>")
    admin = requests.get(f"{BASE}/admin").text
    assert "<script>alert('t')</script>" not in admin
    assert "&lt;script&gt;" in admin


# C009 / C012 — unauthenticated DELETE (open — should FAIL)
def test_delete_requires_auth():
    item_id = _make_item()
    r = requests.delete(f"{BASE}/items/{item_id}")
    assert r.status_code in (401, 403), "DELETE accepted with no auth (C009/C012 open)"


# C009 — PATCH ownership (open — should FAIL)
def test_patch_requires_ownership():
    item_id = _make_item(seller="owner-a")
    r = requests.patch(f"{BASE}/items/{item_id}", json={"is_sold": True})
    assert r.status_code in (401, 403), "PATCH accepted with no auth/ownership (C009 open)"


# C013 — CORS (open — should FAIL)
def test_cors_not_wildcard():
    r = requests.get(f"{BASE}/items", headers={"Origin": "http://evil.example"})
    assert r.headers.get("access-control-allow-origin") != "*", "CORS wildcard (C013 open)"


# C014 — version header (fixed)
def test_no_version_header():
    r = requests.get(f"{BASE}/items")
    assert "x-powered-by" not in {k.lower() for k in r.headers}


# C015 — error handling (adequate)
def test_errors_are_generic():
    r = requests.get(f"{BASE}/items/notanumber")
    assert r.status_code < 500
    assert "Traceback" not in r.text


# C022 — price must be positive
def test_price_must_be_positive():
    r = requests.post(f"{BASE}/items", json={
        "title": "bad", "description": "x", "price": -5,
        "category": "Books", "seller_name": "t"})
    assert r.status_code == 400


# C022 — required fields enforced
def test_required_fields_enforced():
    r = requests.post(f"{BASE}/items", json={"title": "only title"})
    assert r.status_code == 400