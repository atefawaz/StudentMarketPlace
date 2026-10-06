# C024 — Automated Security Test Suite

A pytest suite (backend/tests/test_security.py) that asserts the secure
behaviour for each audit finding. Passing = fixed; failing = still vulnerable.

File: backend/tests/test_security.py (9 tests)
Evidence: C024-tests.png

## Coverage
| Test | Finding | Asserts |
|------|---------|---------|
| test_sqli_search_no_injection | C007 | SQLi payload does not 500 / leak |
| test_xss_admin_escapes_script | C008 | script payload returned escaped |
| test_delete_requires_auth | C009/C012 | DELETE rejects unauth caller (401/403) |
| test_patch_requires_ownership | C009 | PATCH rejects non-owner (401/403) |
| test_cors_not_wildcard | C013 | CORS does not return * |
| test_no_version_header | C014 | no X-Powered-By header |
| test_errors_are_generic | C015 | malformed input is a clean 4xx |
| test_price_must_be_positive | C022 | negative price rejected |
| test_required_fields_enforced | C022 | missing fields rejected |

## Result
6 passed, 3 failed.

Passed (fixes verified): C007, C008, C014, C015, and the two validation checks.
Failed (still open): C009/C012 (DELETE returns 200 with no auth), C009 (PATCH
returns 200 with no ownership check), C013 (CORS returns
access-control-allow-origin: *).

The three failures are the suite correctly detecting the unremediated findings.
As SE lands the auth and CORS fixes, those tests will flip to passing, so the
suite doubles as a remediation tracker.

## How to run
    cd backend
    export DB_PASSWORD=<pw>
    # server running on :5000
    pytest tests/test_security.py -v