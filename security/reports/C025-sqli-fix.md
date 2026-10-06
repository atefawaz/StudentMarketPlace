# C025 — SQL Injection Fix (verification)

C007 (SQLi in /items/search) was remediated by SE in two steps (issue #100):
initial parameterisation (commit 090b628a36), then a follow-up removing the
redundant f-string flagged in the C016 review.

## The fix
backend/app.py line 168 — search_items() now uses a parameterised query with a
plain string:

    "SELECT * FROM items WHERE title LIKE %s OR description LIKE %s ORDER BY created_at DESC",
    (f"%{q}%", f"%{q}%")

Input is passed as parameter values via %s placeholders, not interpolated into
the SQL text. The query string is a plain string (no f-prefix), so there is no
latent risk of accidental interpolation reintroducing injection.

## Verification
- Confirmed in source: plain parameterised query, no f-string on the SQL text
  (grep on app.py line 168).
- test_security.py::test_sqli_search_no_injection PASSES (evidence:
  C025-sqli-fix-verified.png).

## Status
Fixed and verified, including the C016 follow-up (redundant f-string removed).