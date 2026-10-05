"""
Tests for the /auth endpoints: register, login and current user (/auth/me).
"""

import base64
import json
from datetime import datetime, timedelta, timezone

import jwt
import pytest

import auth
from models import get_seller_by_username

VALID_USER = {
    "username": "alice_test",
    "password": "correct horse battery staple",
    "display_name": "Alice Test",
    "email": "alice.test@epita.fr",
}


# ---------------------------------------------------------------------------
# Helpers and fixtures
# ---------------------------------------------------------------------------

def register(client, **overrides):
    return client.post("/auth/register", json={**VALID_USER, **overrides})


def login(client, username=VALID_USER["username"], password=VALID_USER["password"]):
    return client.post("/auth/login", json={"username": username, "password": password})


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}


def assert_unauthorized(response):
    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"] == "Bearer"


def forge_token(sub, key: str | None = auth.SECRET_KEY, algorithm="HS256", with_exp=True):
    """Build a token by hand, bypassing create_token."""
    claims: dict[str, str | datetime] = {"sub": str(sub)}
    if with_exp:
        claims["exp"] = datetime.now(timezone.utc) + timedelta(minutes=5)
    return jwt.encode(claims, key, algorithm=algorithm)


def _b64(data: dict) -> str:
    raw = json.dumps(data).encode()
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


@pytest.fixture
def seller(client):
    response = register(client)
    assert response.status_code == 201
    return response.json()


@pytest.fixture
def token(client, seller):
    response = login(client)
    assert response.status_code == 200
    return response.json()["access_token"]


# ---------------------------------------------------------------------------
# POST /auth/register
# ---------------------------------------------------------------------------

def test_register_success(client):
    response = register(client)

    assert response.status_code == 201
    body = response.json()
    assert set(body) == {"id", "username", "display_name", "email", "created_at"}
    assert body["username"] == "alice_test"
    assert body["display_name"] == "Alice Test"
    assert body["email"] == "alice.test@epita.fr"

    # The password is stored as a bcrypt hash, never in clear text
    stored = get_seller_by_username("alice_test")
    assert stored != None
    assert stored["password_hash"] != VALID_USER["password"]
    assert stored["password_hash"].startswith("$2b$")
    assert auth.verify_password(VALID_USER["password"], stored["password_hash"])


def test_register_duplicate_username(client, seller):
    response = register(client, email="someone.else@epita.fr")

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already taken"


def test_register_duplicate_username_ignores_case(client, seller):
    assert register(client, username="ALICE_TEST").status_code == 409


@pytest.mark.parametrize(
    "overrides",
    [
        {"password": "short"},
        {"password": "é" * 40},  # 40 characters but 80 bytes: over bcrypt's limit
        {"username": "ab"},  # too short
        {"username": "bad name!"},  # invalid characters
        {"email": "not-an-email"},
        {"display_name": "   "},  # blank after stripping
        {"role": "admin"},  # unknown field (extra="forbid")
    ],
    ids=[
        "short_password",
        "password_over_72_bytes",
        "short_username",
        "invalid_username_chars",
        "invalid_email",
        "blank_display_name",
        "unknown_field",
    ],
)
def test_register_rejects_invalid_input(client, overrides):
    # 400 (not 422) because app.py maps validation errors to 400
    assert register(client, **overrides).status_code == 400


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

def test_login_success(client, seller):
    response = login(client)

    assert response.status_code == 200
    body = response.json()
    assert body["token_type"] == "bearer"
    claims = jwt.decode(body["access_token"], auth.SECRET_KEY, algorithms=[auth.ALGORITHM])
    assert claims["sub"] == str(seller["id"])


def test_login_username_is_case_insensitive(client, seller):
    assert login(client, username="ALICE_TEST").status_code == 200


@pytest.mark.parametrize(
    "username, password",
    [
        ("alice_test", "wrong password!"),  # wrong password
        ("nobody", "correct horse battery staple"),  # unknown user
    ],
    ids=["wrong_password", "unknown_user"],
)
def test_login_failure(client, seller, username, password):
    response = login(client, username, password)

    assert_unauthorized(response)
    # Identical message in both cases: no username enumeration
    assert response.json()["detail"] == "Invalid username or password"


# ---------------------------------------------------------------------------
# GET /auth/me
# ---------------------------------------------------------------------------

def test_me_returns_current_seller(client, seller, token):
    response = client.get("/auth/me", headers=auth_header(token))

    assert response.status_code == 200
    assert response.json() == seller


def test_me_returns_the_token_owner(client, seller):
    assert register(client, username="bob_test", email="bob.test@epita.fr").status_code == 201
    bob_token = login(client, "bob_test").json()["access_token"]

    response = client.get("/auth/me", headers=auth_header(bob_token))

    assert response.status_code == 200
    assert response.json()["username"] == "bob_test"


def test_me_without_token(client):
    response = client.get("/auth/me")

    assert_unauthorized(response)
    assert response.json()["detail"] == "Not authenticated"


def test_me_with_wrong_auth_scheme(client, seller):
    response = client.get("/auth/me", headers={"Authorization": "Basic dXNlcjpwYXNz"})

    assert_unauthorized(response)


def test_me_with_expired_token(client, seller, monkeypatch):
    # create_token reads this module-level setting at call time, so a negative
    # lifetime yields a token that is already expired.
    monkeypatch.setattr(auth, "ACCESS_TOKEN_EXPIRE_MINUTES", -1)
    expired = auth.create_token(seller["id"])

    response = client.get("/auth/me", headers=auth_header(expired))

    assert_unauthorized(response)
    assert response.json()["detail"] == "Token has expired"


def test_me_with_tampered_payload(client, seller, token):
    header, _payload, signature = token.split(".")
    claims = jwt.decode(token, options={"verify_signature": False})
    claims["sub"] = str(seller["id"] + 1)  # try to impersonate another seller
    tampered = ".".join([header, _b64(claims), signature])

    response = client.get("/auth/me", headers=auth_header(tampered))

    assert_unauthorized(response)
    assert response.json()["detail"] == "Invalid token"


FORGERIES = {
    "wrong_key": lambda sid: forge_token(sid, key="x" * 32),
    "alg_none": lambda sid: forge_token(sid, key=None, algorithm="none"),
    "missing_exp": lambda sid: forge_token(sid, with_exp=False),
    "non_numeric_sub": lambda sid: forge_token("abc"),
    "garbage": lambda sid: "not.a.jwt",
}


@pytest.mark.parametrize("make_token", FORGERIES.values(), ids=FORGERIES.keys())
def test_me_with_invalid_token(client, seller, make_token):
    response = client.get("/auth/me", headers=auth_header(make_token(seller["id"])))

    assert_unauthorized(response)
    assert response.json()["detail"] == "Invalid token"


def test_me_with_token_for_deleted_seller(client):
    # Valid signature and expiry, but the seller id doesn't exist
    ghost_token = auth.create_token(999999)

    assert_unauthorized(client.get("/auth/me", headers=auth_header(ghost_token)))