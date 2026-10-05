# C026 — Authentication + IDOR Fix (verification)

C009/C012 (missing auth + IDOR on DELETE/PATCH) were remediated by SE
(issue #107, commit 41c0c0e423).

## The fix
A JWT bearer-token auth layer was added (auth.py: get_current_user). State-
changing routes now require authentication:
- POST /items requires a valid token; the seller is taken from the token
  (seller_id / display_name), not from client input.
- DELETE and PATCH /items/{id} use a require_item_owner dependency: 401 if the
  token is missing/invalid, 404 if the item doesn't exist, 403 if it belongs to
  another seller.

This closes both angles: no-auth access AND the absence of an ownership check.
Removing the client-supplied seller_name also prevents ownership spoofing.

## Verification
Re-ran the security test suite after the fix landed:
- test_delete_requires_auth PASSES (previously 200 with no credentials; now 401).
- test_patch_requires_ownership PASSES (previously 200; now requires auth).
- POST /items now returns 401 without a token.

Before the fix, an anonymous caller could delete/modify any item by id (C019:
25/25 modifiable). SE's test_items.py additions also cover forged/expired tokens
and non-owner 403 responses.

## Status
Fixed and verified.