# Student Marketplace

A campus marketplace where students can buy and sell second-hand items. Built with a **Python/FastAPI** backend and a native mobile client (**Android/Java** or **iOS/Swift**).

This project is approximately **60% complete**. Your challenge: finish the remaining features during the build week.

---

## Architecture

```
┌──────────────┐         HTTP/JSON         ┌──────────────────┐
│              │  GET  /items              │                  │
│   Android    │  GET  /items/{id}        │   FastAPI        │
│     or       │◄─────────────────────────►│   Backend        │
│    iOS       │  POST /items             │   (Python)       │
│   Client     │  PATCH /items/{id} [TODO]│                  │
│              │                           │   MySQL DB       │
└──────────────┘                           └──────────────────┘
```

### What works now

- **Backend:** `GET /items`, `GET /items/{id}`, `POST /items` are fully functional.
- **Database:** MySQL with a seed script (20 realistic items across 4 categories).
- **Android:** Main screen displays the item list from the API. Navigation wired to detail and create screens.
- **iOS:** Table view displays items. Navigation wired to detail and create screens.

### What you need to build

See the [TODOs](#todos) section below.

---

## Prerequisites

| Tool | Version |
|------|---------|
| Python | 3.10+ |
| pip | latest |
| MySQL | 8.0+ |
| Android Studio | 2023.1+ (for Android track) |
| Xcode | 15+ (for iOS track) |

---

## Setup

### Backend

```bash
cd backend

# Make sure MySQL is running and accessible (default: root@localhost:3306)

# Create a virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Seed the database with sample data (creates the DB and table automatically)
python seed.py

# Start the server
uvicorn app:app --reload --port 5000
```

The API is now available at `http://localhost:5000`.

### Android

1. Open the `android/` folder in **Android Studio**.
2. Let Gradle sync.
3. Make sure the backend is running on port 5000.
4. Run on an emulator (the app uses `10.0.2.2:5000` to reach host localhost).

### iOS

See [`ios/README-iOS.md`](ios/README-iOS.md) for detailed Xcode setup instructions.

---

## API Documentation

### `GET /items`

Returns all items, newest first.

```json
[
  {
    "id": 1,
    "title": "Introduction to Algorithms (Cormen, 4th ed.)",
    "description": "Hardcover, some highlighting in chapters 1-12.",
    "price": 35.0,
    "category": "Books",
    "image_url": null,
    "seller_name": "Alice Martin",
    "created_at": "2026-03-28 10:00:00",
    "is_sold": false
  }
]
```

### `GET /items/{id}`

Returns a single item. **404** if not found.

### `POST /items`

Create a new listing.

**Request body:**
```json
{
  "title": "My Item",
  "description": "Optional description",
  "price": 25.00,
  "category": "Books",
  "seller_name": "Your Name"
}
```

**Response:** `201 Created` with the full item object.

---

## Running Tests

```bash
cd backend
pytest tests/ -v
```

You should see **4 passing** and **3 failing** tests. The failing tests correspond to features you need to implement.

---

## TODOs

Each TODO includes **acceptance criteria** so you know when it is done.

### TODO 1 — Item Detail Screen

> **Goal:** Tapping an item in the list opens a detail view with all item info.

**Acceptance criteria:**
- Detail screen loads data from `GET /items/{id}`.
- Displays: title, description, price, category, seller name, posted date.
- If the item is sold, a visible "SOLD" badge is shown.
- Back navigation returns to the list.

**Files to edit:**
- Android: `ItemDetailActivity.java`, `activity_item_detail.xml`
- iOS: `ItemDetailViewController.swift`

---

### TODO 2 — Create Item Form + Validation

> **Goal:** The "+" button opens a form that lets the user post a new item.

**Acceptance criteria:**
- Form fields: title, description, price, category, seller name.
- Validation: title, price, category, and seller name are required. Price must be > 0.
- On submit, `POST /items` is called. On success, navigate back to the list. On error, display an error message.
- The new item appears in the list after returning.

**Files to edit:**
- Android: `CreateItemActivity.java`
- iOS: `CreateItemViewController.swift`

---

### TODO 3 — Filter by Category

> **Goal:** Users can filter the item list to show only one category.

**Acceptance criteria:**
- `GET /items?category=Books` returns only items where `category == "Books"`.
- The mobile app provides a UI control (dropdown, tab bar, or chips) to select a category.
- Selecting "All" (or equivalent) shows all items.
- Test `test_filter_by_category` passes.

**Files to edit:**
- Backend: `app.py`, `models.py`
- Android: `MainActivity.java`
- iOS: `ItemListViewController.swift`

---

### TODO 4 — Sort by Price / Date

> **Goal:** Users can sort items by price or date.

**Acceptance criteria:**
- `GET /items?sort=price_asc` returns items sorted by price ascending.
- Supported values: `price_asc`, `price_desc`, `date_asc`, `date_desc`.
- The mobile app provides a sort toggle or dropdown.
- Test `test_sort_items` passes.

**Files to edit:**
- Backend: `app.py`, `models.py`
- Android: `MainActivity.java`
- iOS: `ItemListViewController.swift`

---

### TODO 5 — Mark as Sold

> **Goal:** A seller can mark their item as sold.

**Acceptance criteria:**
- `PATCH /items/{id}` accepts `{"is_sold": true}` and updates the item.
- The detail screen shows a "Mark as sold" button (hidden if already sold).
- After marking as sold, the item appears dimmed in the list with a "SOLD" badge.
- Test `test_mark_as_sold` passes.

**Files to edit:**
- Backend: `app.py`, `models.py`
- Android: `ItemDetailActivity.java`, `activity_item_detail.xml`
- iOS: `ItemDetailViewController.swift`

---

### TODO 6 (Bonus) — Full-Text Search

> **Goal:** Users can search items by keyword.

**Acceptance criteria:**
- `GET /items?q=keyboard` returns items whose title or description contain "keyboard" (case-insensitive).
- The mobile app has a search bar at the top of the item list.
- Results update as the user types (or on submit).

**Files to edit:**
- Backend: `app.py`, `models.py`
- Android: `MainActivity.java`
- iOS: `ItemListViewController.swift`

---

## Project Structure

```
02-student-marketplace/
├── backend/
│   ├── app.py              # FastAPI application
│   ├── database.py         # MySQL connection helpers
│   ├── models.py           # Pydantic schemas + DB queries
│   ├── seed.py             # Seed 20 sample items
│   ├── requirements.txt    # Python dependencies
│   └── tests/
│       ├── conftest.py     # Test fixtures (test MySQL DB, TestClient)
│       └── test_items.py   # 7 tests (4 pass, 3 fail = your TODOs)
├── android/
│   ├── app/
│   │   └── src/main/
│   │       ├── java/com/epita/marketplace/
│   │       │   ├── MainActivity.java
│   │       │   ├── ItemDetailActivity.java      # TODO
│   │       │   ├── CreateItemActivity.java      # TODO
│   │       │   ├── model/Item.java
│   │       │   ├── adapter/ItemAdapter.java
│   │       │   └── api/ApiClient.java
│   │       ├── res/layout/
│   │       │   ├── activity_main.xml
│   │       │   ├── activity_item_detail.xml
│   │       │   ├── activity_create_item.xml
│   │       │   └── item_card.xml
│   │       └── AndroidManifest.xml
│   ├── app/build.gradle
│   ├── build.gradle
│   └── settings.gradle
├── ios/
│   ├── StudentMarketplace/
│   │   ├── Models/Item.swift
│   │   ├── Services/APIClient.swift
│   │   └── Views/
│   │       ├── ItemListViewController.swift
│   │       ├── ItemDetailViewController.swift   # TODO
│   │       └── CreateItemViewController.swift   # TODO
│   ├── StudentMarketplace/Info.plist
│   └── README-iOS.md
├── .gitignore
└── README.md
```


---

## SE TODOs (40)


### Core (01-15)

| Code | TODO |
|------|------|
| SMKT-S001 | [API] GET /items/:id returns all fields |
| SMKT-S002 | [Mobile] Detail screen: call API, populate fields |
| SMKT-S003 | [Mobile] Format price + relative date |
| SMKT-S004 | [Mobile] SOLD overlay if is_sold=true |
| SMKT-S005 | [Mobile] Loading spinner, 404 handling |
| SMKT-S006 | [API] POST /items validation (title, price, category) |
| SMKT-S007 | [API] Return 400 with field errors |
| SMKT-S008 | [Mobile] Creation form: title, desc, price, category |
| SMKT-S009 | [Mobile] Category dropdown (Books, Electronics, etc.) |
| SMKT-S010 | [Mobile] Client validation with inline errors |
| SMKT-S011 | [Mobile] On 201, navigate back, item at top |
| SMKT-S012 | [API] GET /categories (DISTINCT) |
| SMKT-S013 | [API] Filter GET /items by category param |
| SMKT-S014 | [Mobile] Horizontal chip row from GET /categories |
| SMKT-S015 | [Mobile] Chip filtering, highlight active, empty state |

### Intermediate (16-25)

| Code | TODO |
|------|------|
| SMKT-S016 | [API] Sort param: price_asc/desc, date_asc/desc |
| SMKT-S017 | [API] Combine sort + category filter |
| SMKT-S018 | [Mobile] Sort button + bottom sheet |
| SMKT-S019 | [Mobile] Persist sort preference |
| SMKT-S020 | [API] PATCH /items/:id {is_sold} |
| SMKT-S021 | [Mobile] 'Mark as Sold' button on detail |
| SMKT-S022 | [Mobile] Confirmation dialog + SOLD overlay |
| SMKT-S023 | [Mobile] List refreshes on back |
| SMKT-S024 | [Mobile] Un-mark: 'Mark as Available' |
| SMKT-S025 | [API] Search param (LIKE title+desc) |

### Advanced (26-35)

| Code | TODO |
|------|------|
| SMKT-S026 | [Mobile] Search bar with debounce + clear |
| SMKT-S027 | [API] Pagination: page + limit + total_count |
| SMKT-S028 | [Mobile] Infinite scroll |
| SMKT-S029 | [Mobile] Pull-to-refresh |
| SMKT-S030 | [Mobile] List cards: image, title, price, badge, status |
| SMKT-S031 | [Mobile] 'Contact Seller' email button |
| SMKT-S032 | [Mobile] Share button on detail |
| SMKT-S033 | [API] GET /items/:id/similar (same category, limit 5) |
| SMKT-S034 | [Mobile] Similar Items section on detail |
| SMKT-S035 | [Mobile] Similar item tap navigates to detail |

### Polish (36-40)

| Code | TODO |
|------|------|
| SMKT-S036 | [Mobile] Image loading + placeholders |
| SMKT-S037 | [Mobile] Empty list: 'No items yet' CTA |
| SMKT-S038 | [Mobile] Item count badge on category chips |
| SMKT-S039 | [Mobile] 'My Listings' section |
| SMKT-S040 | [Mobile] Final polish: card design, margins, responsive |

## CS TODOs (30)


### Threat Modeling (C001-C006)

| Code | TODO |
|------|------|
| SMKT-C001 | Architecture diagram + data flows + trust boundaries |
| SMKT-C002 | Endpoint inventory (method, inputs, auth, sensitivity) |
| SMKT-C003 | STRIDE analysis on main flow |
| SMKT-C004 | Attack surface mapping (all untrusted inputs) |
| SMKT-C005 | Attack tree (3+ paths, AND/OR nodes) |
| SMKT-C006 | 1-page threat assessment (top 5 risks) |

### Code Review / Bug Bounty (C007-C016)

| Code | TODO |
|------|------|
| SMKT-C007 | Find SQL Injection (CWE-89) |
| SMKT-C008 | Find Stored XSS (CWE-79) |
| SMKT-C009 | Find IDOR (CWE-639) |
| SMKT-C010 | Find hardcoded secrets (CWE-798) |
| SMKT-C011 | Find weak password hashing (CWE-328) |
| SMKT-C012 | Audit missing authentication (CWE-306) |
| SMKT-C013 | Analyze CORS configuration |
| SMKT-C014 | Find debug mode exposure (CWE-489) |
| SMKT-C015 | Review error handling (CWE-209) |
| SMKT-C016 | Audit SE teammates' code (2+ bug reports) |

### Security Testing (C017-C024)

| Code | TODO |
|------|------|
| SMKT-C017 | SQLi exploit script |
| SMKT-C018 | XSS exploit (3 payloads) |
| SMKT-C019 | IDOR enumeration script |
| SMKT-C020 | Rate limit / DoS test |
| SMKT-C021 | Automated scan (nmap + Python) |
| SMKT-C022 | API fuzzer |
| SMKT-C023 | Project-specific exploit (Werkzeug/pickle/CSRF/etc.) |
| SMKT-C024 | test_security.py (8+ pytest cases) |

### Deployment & Hardening (C025-C030)

| Code | TODO |
|------|------|
| SMKT-C025 | Fix SQL Injection (parameterized queries) |
| SMKT-C026 | Add authentication + fix IDOR |
| SMKT-C027 | Secure configuration (debug, secrets, passwords) |
| SMKT-C028 | Security headers + rate limiting |
| SMKT-C029 | Structured logging + alerting |
| SMKT-C030 | Final 5-page audit report |

---

## Expert TODOs (AI-resistant, optional, 20)

These 20 tasks (10 SE, 10 CS) are **not counted** in the 40/30 base TODOs above and are not
required to pass the Challenge Week. They exist for teams that finish early, or for teachers who
want a harder bar. Each one requires actually **running** something against the live system
(concurrent requests, timing measurements, a generated dataset, a live SQLi extraction) and
producing real evidence, not a plausible-sounding write-up: a prompt to an AI assistant can draft
code for any of these, but it cannot observe the running system, so the draft is never enough on
its own. That gap between "code that compiles" and "an actually reproduced result" is the point.

### SE, Expert (SX01-SX10)

| Code | TODO |
|------|------|
| SMKT-SX01 | **Race condition on "mark as sold".** Once S020 (`PATCH /items/:id`) exists, it almost certainly does a check-then-update in Python, not an atomic one. Fire 20 concurrent `PATCH /items/<id>` with `{"is_sold": true}` at the same item and reproduce more than 1 request reading "not yet sold" before the fix. Fix with a single conditional `UPDATE items SET is_sold = 1 WHERE id = %s AND is_sold = 0` and check `cursor.rowcount`; re-run the same 20-concurrent script 10 times: exactly 1 success every time. |
| SMKT-SX02 | **Idempotent listing creation.** `items` has no uniqueness constraint at all (see `database.py` lines 36-47: only `id INT AUTO_INCREMENT PRIMARY KEY`), so a double-tap on "Post" or a mobile network retry silently creates two identical listings. Design an idempotency mechanism (client-generated idempotency key stored server-side, or a content hash on `title`+`seller_name`+`price` with a short dedup window) and prove it against 20 rapid duplicate `POST /items` submissions with identical bodies. |
| SMKT-SX03 | **Sub-second sort ties, made concrete.** `created_at` is a MySQL `TIMESTAMP` (`database.py` line 44): 1-second resolution, no microseconds. Once S016 (`sort=date_desc`) is implemented, insert 5 items in a tight loop (well under 1 second) and show the API returning a different relative order across repeated `GET /items?sort=date_desc` calls for items with an identical `created_at` value. Fix with a deterministic tiebreaker (`ORDER BY created_at DESC, id DESC`) and prove the order is now stable across 20 repeated fetches. |
| SMKT-SX04 | **Stable pagination under concurrent inserts.** S027 (pagination) does not exist yet in `app.py`. Implement keyset (cursor) pagination on `GET /items` ordered by `(created_at, id)`, such that a script inserting a new item *between* two page fetches never causes a client to see a skipped or duplicated item. Prove the invariant with that script, not just a description of the algorithm. |
| SMKT-SX05 | **Offline-first item creation.** On Android or iOS, posting a listing while offline must queue the request, retry automatically on reconnect, and never show a false "Posted!" state if the server later rejects it (e.g. a 422 from `ItemCreate`'s `price: gt=0` validation, `models.py` line 18, once your client sends a bad value it had cached). Demo live by toggling airplane mode mid-submission. |
| SMKT-SX06 | **Measured performance budget for "Similar Items".** S033 (`GET /items/:id/similar`) has to query by `category`, which has no index (`database.py` lines 36-47: no `INDEX` or `KEY` on any column besides the primary key). Generate 5,000+ synthetic items yourself directly with SQL (`seed.py`'s `seed()` only inserts its fixed 20-item list and exits early if the table is non-empty, so it will not get you there) and get the similar-items endpoint under a stated p95 latency using a real benchmarking tool (`wrk`/`hey`/`locust`). Include the `EXPLAIN` output before and after adding an index on `category`. |
| SMKT-SX07 | **Adversarial input fuzzing across the validation gap.** `POST /items` is validated by the `ItemCreate` Pydantic model (`models.py` lines 14-21), but `PATCH /items/{item_id}` (`app.py` lines 119-133) takes a raw `dict` with **zero schema**, so it can set `is_sold` to any JSON value (a string, `null`, a float, a nested object) or overwrite `price`/`title` with anything at all. Write a property-based test (Hypothesis) that fuzzes PATCH bodies and asserts the item table can never end up in a state `GET /items/{id}` cannot itself represent faithfully (e.g. `is_sold` outside {0,1}, a `price` the DB silently truncated). |
| SMKT-SX08 | **Real broken-image handling.** Every seeded item has `image_url: null` (`seed.py`, all 20 entries), so nobody on the team has actually seen a broken image render. Construct 5 real broken-URL fixtures yourself (404, connection timeout, malformed URL, a URL that returns HTML instead of an image, an oversized image) and build verified fallback UI on Android and iOS against each, not just "it compiles". |
| SMKT-SX09 | **Leak-free "posted X ago" label.** The relative-date label implied by the seller/listing UI must stay correct across a DST transition in dates you seed yourself, and must not leak a repeating timer: survive an 8-hour idle UI test (Espresso/XCTest) with measured, flat memory usage. |
| SMKT-SX10 | **Load-test your own SX01 fix.** Simulate 300+ concurrent "buyers" hammering `PATCH /items/<id>` with `{"is_sold": true}` on the same item (a distributed script, not a single-machine loop) and report actual numbers, not estimates, on whether the atomic-update fix from SX01 holds under this specific load profile. |

### CS, Expert (CX01-CX10)

| Code | TODO |
|------|------|
| SMKT-CX01 | **End-to-end exploit chain.** One script: use the SQL injection in `GET /items/search` (`app.py` line 80, an f-string dropped straight into `LIKE '%{q}%'`) to `UNION SELECT` the `username`/`password`/`email` columns out of the `sellers` table created by `seed_users()` (`seed.py` lines 235-261), then use the unauthenticated `DELETE /items/{item_id}` (`app.py` lines 107-115, no auth check at all) to remove every listing posted under one of the extracted seller names. Report how many listings were destroyed. |
| SMKT-CX02 | **Black-box endpoint discovery.** The README's "API Documentation" section only documents `GET /items`, `GET /items/{id}`, and `POST /items`. `GET /items/search`, `PATCH /items/{id}`, `DELETE /items/{id}`, `GET /admin`, and `POST /sellers/register` all exist in the running server but are undocumented. Find them by dynamic discovery against the live server (path/method fuzzing), as in a real black-box pentest, not by reading `app.py`. Submit the raw request/response pairs as evidence. |
| SMKT-CX03 | **Second-order injection via a JSON key, not a value.** `PATCH /items/{item_id}` (`app.py` lines 119-133) builds `UPDATE items SET {key} = %s` directly from the request body's own keys, with no allowlist. Standard SQLi payloads in the *values* do nothing here. Craft a malicious JSON **key** (not value) in the PATCH body that breaks out of the intended `UPDATE` statement, and show its effect on data outside the targeted row. |
| SMKT-CX04 | **Extract real plaintext credentials, then prove impact.** `seed_users()` (`seed.py` lines 235-261) stores seller passwords in **cleartext**: no hash function of any kind is called anywhere in this codebase (there is no `login` endpoint either). Extract the 3 real seeded credentials from the live `sellers` table via your own SQLi exploit (not the values printed in this repository, since a reseeded database may differ), then demonstrate practical impact by reusing the admin credentials against a login mechanism an SE teammate builds later; coordinate timing with them and record the result. |
| SMKT-CX05 | **Tuned detection rule.** Write a fail2ban filter or a small log-tailer that flags your own SQLi payloads against `GET /items/search`, with zero false positives on a set of realistic legitimate search queries you write yourself (accented titles, an apostrophe like "Levi's", a percent sign). Prove both the true-positive and the true-negative with real log samples from the running server, not a synthetic example. |
| SMKT-CX06 | **Timing side-channel.** Determine whether `GET /items/{item_id}` or `DELETE /items/{item_id}` leaks the existence of an item through response-time alone, independent of the 404/200 status code. Requires real statistical measurement (n≥100 per class, mean/stddev, a significance test) against the live server, not a theoretical claim. |
| SMKT-CX07 | **Measured DoS breaking point.** Generate 50,000+ synthetic items yourself directly with SQL (`seed.py`'s `seed()` inserts a fixed 20-item list and exits early once the table is non-empty, so it cannot get you there). Find the actual request rate at which `GET /items/search`'s unbounded `LIKE '%...%'` over an unindexed `title`/`description` (`database.py` lines 36-47) saturates a core enough to make `GET /items` time out. Propose a fix and re-run the same load test to validate it. |
| SMKT-CX08 | **Reachable-CVE audit of `requirements.txt`.** For each pin (`fastapi>=0.110,<1.0`, `uvicorn>=0.29,<1.0`, `pydantic>=2.0,<3.0`, `mysql-connector-python>=9.0,<10.0`), determine whether a known CVE is actually reachable from this codebase's usage, not just "the CVE exists somewhere in the package". Note that `PoweredByMiddleware` (`app.py` lines 26-30) hardcodes the response header `X-Powered-By: FastAPI/0.104.1 Python/3.11`, a version that does not even satisfy the `requirements.txt` pin: confirm the *actual* installed FastAPI and Python versions on the running server (e.g. `pip show fastapi`) before trusting that header for your CVE lookup. Build a working PoC if a CVE is reachable; if none is, prove that negative result with evidence. |
| SMKT-CX09 | **Three-endpoint attack chain + timeline reconstruction.** `GET /admin` (`app.py` lines 89-102) builds its HTML with an f-string that drops `item['title']`, `item['description']`, and `item['seller_name']` straight into the page with no escaping. Chain a `POST /items` carrying an XSS payload in `title`, the unauthenticated `DELETE /items/{item_id}`, and `GET /admin` to deface the admin page and then wipe the evidence in one scenario. Reconstruct a timeline of your own attack using only MySQL's `created_at` values and uvicorn's default request logs, and note as a finding that `created_at`'s 1-second resolution (`database.py` line 44) limits how precisely that timeline can actually be reconstructed, since no structured logging exists to do better. |
| SMKT-CX10 | **Red-team your own Thursday patch.** After the team's hardening lands (parameterized PATCH, auth on DELETE, escaped admin HTML), try to bypass your own fixes: parameter pollution on `q`, alternate URL encodings, an HTTP verb override header, a trailing slash on `/items/search/`, route case variation, and JSON key casing tricks against whatever allowlist was added to close CX03. Either find a working bypass, or produce a documented, actually-executed test matrix proving none of these worked. |
