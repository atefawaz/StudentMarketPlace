# C019 — IDOR Enumeration Script

Enumeration script for the IDOR on /items/{id} (finding C009).

Script: security/exploits/c019_idor_enum.py
Evidence: C019-idor-enum.png

## Method
Fetches every item id from GET /items, then sends a PATCH to each one (flipping
is_sold) with no credentials. PATCH is used rather than DELETE so the
demonstration is reversible and does not destroy data. Each accepted request
proves the item can be modified by an unauthenticated, non-owner caller.

## Result
    found 25 items
    id 1..27: PATCH accepted (no auth, no ownership) -> IDOR
    25/25 items modifiable by an unauthenticated caller

Every one of the 25 items was modified by an anonymous caller. There is no
authentication and no ownership check on PATCH /items/{id}, so an attacker can
tamper with the entire catalogue by iterating ids.

## Impact
Complete, unrestricted modification of all listings by any anonymous user. The
same exposure applies to DELETE /items/{id} (which would destroy rather than
modify). Confirms and quantifies finding C009.

## Remediation
Require authentication and an ownership check on PATCH and DELETE (reject with
403 if the item's seller is not the caller). See C009 / C026.