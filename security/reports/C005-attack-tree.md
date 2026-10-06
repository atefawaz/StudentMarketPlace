# C005 — Attack Tree

Goal: compromise the marketplace (steal credentials / control data).
OR = any child achieves the parent. AND = all children required.

    GOAL: Compromise the marketplace
    |
    ├── OR 1: Steal seller/admin credentials
    |     |
    |     └── AND (both needed)
    |          ├── Reach the search endpoint
    |          └── Inject UNION SELECT on sellers via q  [C007]
    |               -> passwords are plaintext, so readable directly  [C011]
    |
    ├── OR 2: Destroy or tamper with listings
    |     |
    |     ├── DELETE /items/{id} with no auth  [C012]
    |     └── PATCH /items/{id} to overwrite any field, no auth/ownership  [C012, CX03]
    |
    ├── OR 3: Run code in the admin's browser
    |     |
    |     └── AND (both needed)
    |          ├── Store an XSS payload via POST /items  [C008]
    |          └── Admin opens /admin, payload executes  [C008]
    |               -> can then drive the unauth DELETE as the admin  [C012]
    |
    └── OR 4: Reconnaissance
          |
          ├── Read version from X-Powered-By header  [C014]
          └── Read the hardcoded secret from source  [C010]

## Notes
- OR 1 and OR 3 are AND-chains (two steps must line up); OR 2 and OR 4 are
  single-step OR paths (any one works alone).
- Every leaf is backed by a documented finding, and OR 1, OR 2, OR 3 have been
  reproduced against the running app.
- The highest-value path is OR 1: it yields the admin credential, and because
  passwords are plaintext there is no cracking step.