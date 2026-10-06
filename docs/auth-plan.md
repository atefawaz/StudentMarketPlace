# Authentication & Authorization Plan

JWT authentication for the FastAPI backend and a simple login/register + ownership model in the iOS app. Issue codes use the prefix `SMKT-A` so they don't collide with the existing `SMKT-S` (SE) and `SMKT-C` (CS) codes.

This plan delivers **SMKT-C026** ("Add authentication + fix IDOR") and part of **SMKT-C027**.

---

## 1. Current state

**Backend**
- The `sellers` table exists only in `seed_users()` (`seed.py`), with plaintext passwords. `init_db()` and the app never use it.
- Write endpoints are open to anyone:
  - `POST /items` trusts a client-supplied `seller_name` string.
  - `PATCH /items/{id}` and `DELETE /items/{id}` have no owner check.
- `items` has no link to `sellers`.
- `SECRET_KEY = "super-secret-key-123"` is hardcoded in `app.py` and unused.
- `/sellers/register` is a stub that only logs.

**iOS**
- `APIClient` has no auth concept.
- The create form asks for a free-text seller name.
- The "Mark as Sold" button is shown to every user.

**Already done:** S001–S024 and S038; C001–C014 findings. Not done: S039 (My Listings), S031 (Contact Seller).

---

## 2. Design decisions

1. **One access token, no refresh.** HS256, `sub` = seller id, 24h expiry (configurable). After expiry the user logs in again.
2. **Secret from env.** `JWT_SECRET` env var; the server refuses to start without it.
3. **Libraries:** `PyJWT` and `bcrypt` directly. Avoid `passlib` (unmaintained, breaks with recent `bcrypt`).
4. **Login takes JSON**, not the OAuth2 form flow, so iOS can send it easily.
5. **Ownership:** add `items.seller_id` (FK to `sellers`). The server fills `seller_name` from the token; the client no longer sends it.
6. **Public reads:** `GET /items`, `GET /items/{id}`, `GET /categories` stay public. Guests can browse. Create, mark sold and delete require login. The owner check is enforced server-side; hiding buttons in iOS is cosmetic only.
7. **No roles.** No admin role. Drop the seeded `admin` / `admin123` account (a known credential with no special power).
8. **No `ALTER` migration.** `init_db()` uses `CREATE TABLE IF NOT EXISTS`, so every teammate drops `student_marketplace` and re-seeds once.
9. **Out of scope:** `/admin` and `/items/search` stay as they are; they belong to the CS hardening issues (C025/C027).

---

## 3. API contract

Agree on this first so iOS can start in parallel (mocking if needed).

| Endpoint | Request | Success | Errors |
|---|---|---|---|
| `POST /auth/register` | `{username, password (min 8), email?, display_name?}` | `201 {access_token, token_type: "bearer", seller: {id, username, email, display_name}}` | 400 validation, 409 username taken |
| `POST /auth/login` | `{username, password}` | `200`, same body as register | 401 `"Invalid username or password"` (identical message for unknown user and wrong password) |
| `GET /auth/me` | Bearer token | `200 seller` | 401 |
| `POST /items` | Same as today minus `seller_name`; Bearer token | 201 | 401 |
| `PATCH /items/{id}` | Bearer token | As today | 401 no/invalid token, 403 not the owner, 404 |
| `DELETE /items/{id}` | Bearer token | As today | 401 no/invalid token, 403 not the owner, 404 |

`ItemOut` gains `seller_id`.

Validation errors keep the existing 400 format (`{"detail": "Validation failed", "errors": {...}}`).

---

## 4. Issues

### Backend

#### SMKT-A01 — [API] Sellers schema, password hashing, seed

- Move `sellers` into `init_db()` with `UNIQUE(username)`, `password_hash`, `display_name`, `email`.
- Add `items.seller_id INT NULL` with a FK to `sellers`.
- `seed.py` hashes passwords with bcrypt and creates one seller per distinct seeded `seller_name`. Each seeded item gets a `seller_id`. Remove the `admin` account.

**Acceptance criteria**
- After a reset and re-seed, no plaintext password exists in the DB.
- Every seeded item has a `seller_id`.
- Existing tests still pass.

#### SMKT-A02 — [API] JWT auth: register, login, me

*Depends on: A01*

- Add `auth.py` with `hash_password`, `verify_password`, `create_token`, and a `get_current_seller` dependency (`HTTPBearer`).
- Add `POST /auth/register`, `POST /auth/login`, `GET /auth/me`.
- Remove the `/sellers/register` stub and the hardcoded `SECRET_KEY`.
- On login for an unknown user, still run a dummy bcrypt compare so response timing doesn't reveal which usernames exist.

**Acceptance criteria**
- Expired, tampered and missing tokens return 401 with a `WWW-Authenticate: Bearer` header.
- Tests cover register, duplicate username, login success and failure, `me`, and an expired token.
- Startup fails if `JWT_SECRET` is unset; tests set it in `conftest.py`.

#### SMKT-A03 — [API] Protect write endpoints + ownership

*Depends on: A02*

- `POST /items` requires a token and sets `seller_id` and `seller_name` from it. Remove `seller_name` from `ItemCreate` (`extra="forbid"` will reject it if sent).
- `PATCH` and `DELETE` require a token and return 403 unless `items.seller_id` equals the caller's id.
- Add `seller_id` to `ItemOut`.
- Add a `seller_token` fixture to `conftest.py` and fix the existing tests that call write endpoints.

**Acceptance criteria**
- Tests cover 401 without a token, 403 for a non-owner, and success for the owner on PATCH and DELETE.
- README API section documents the auth header and error codes.

### iOS

#### SMKT-A04 — [Mobile] Session layer

*Can start once the contract (section 3) is agreed; mock if the backend isn't ready.*

- Add a small `KeychainStore` for the token (not UserDefaults).
- Add a `Session` singleton holding the current seller, with `login`, `register`, `restore`, `logout`.
- `APIClient` adds the `Authorization: Bearer` header on write calls. A 401 posts a `.sessionExpired` notification; a 403 maps to `APIError.forbidden`.
- Add `APIClient.login`, `register`, `me`.

**Acceptance criteria**
- Token survives an app restart.
- A 401 from any call clears the token.
- Logic is testable without UI.

#### SMKT-A05 — [Mobile] Login / Register screen

*Depends on: A04*

- One `AuthViewController` with a Login/Register toggle, built from the existing `FormTextField` and `FormFieldGroup`.
- Client validation matches the backend: username required, password at least 8 characters.
- Inline errors, including "Username already taken" on 409.

**Acceptance criteria**
- Successful login or register dismisses the screen and updates `Session`.
- A wrong password shows a generic error.

#### SMKT-A06 — [Mobile] App gating and session restore

*Depends on: A05*

- `ItemListViewController` nav bar shows "Log in", or the username with "Log out".
- Tapping "+" while logged out presents the auth screen.
- On launch, `Session.restore()` validates the stored token via `/auth/me`.
- The `.sessionExpired` notification returns the user to a logged-out state with a message.

**Acceptance criteria**
- Guests can browse.
- Logout clears the Keychain.
- An expired token forces re-login without a crash.

#### SMKT-A07 — [Mobile] Authorization in the UI

*Depends on: A03, A06*

- Create form drops the seller name field, shows "Posting as <name>", and no longer sends `sellerName`. Update `CreateItemRequest` and `Item` (add `sellerId`).
- Show "Mark as Sold/Available" only when `item.sellerId == Session.seller.id`.
- Show a clear alert on 403.

**Acceptance criteria**
- A non-owner never sees the button.
- If a non-owner's request is forced through, the app shows the 403 message.

### Docs / QA

#### SMKT-A08 — [Docs/QA] Docs and end-to-end check

- Update the README: setup needs `JWT_SECRET`, reset-DB step, demo accounts, API docs, and the stale "4 passing / 3 failing" line.
- Manual checklist: register, login, post, mark sold, log in as a different user and confirm 403, let the token expire.
- Notify CS to re-test C009, C011, C012 and C026.

### Optional

#### SMKT-A09 — My Listings (same as S039)

`GET /items?mine=true` (token required) plus a list filter in iOS. Cheap once `seller_id` exists.

---

## 5. Order and split

```
A01 → A02 → A03 ──────────────┐
        └─ contract ─→ A04 → A05 → A06 → A07 → A08
```

- **Person 1 (backend):** A01, A02, A03.
- **Person 2 (iOS):** A04, A05, A06, then A07 once A03 is merged.
- **Merge A03 and A07 close together.** Removing `seller_name` from the API is a breaking change; an old iOS build would get 400s until A07 lands.

---

## 6. Coordination with CS

- The C007 PoC (extracting plaintext passwords), and the C009, C011, C012 findings will no longer reproduce after A01/A03. Give CS a heads-up before merging so they can capture "before" evidence and re-test afterwards.
- CX04 (reuse admin credentials against a login built by an SE teammate) depends on this login. Coordinate timing, and note the `admin` account is being removed.
