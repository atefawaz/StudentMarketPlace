# C023 — Project-Specific Exploit: Unauthenticated Mass Deletion

The app's defining weakness is that no endpoint requires authentication. This
exploit chains item enumeration with the unauthenticated DELETE endpoint to let
an anonymous attacker destroy listings — the most damaging attack specific to
this application's design.

Script: security/exploits/c023_mass_delete.py
Evidence: C023-mass-delete.png

## Why this is the project-specific exploit
Generic OWASP bugs aside, the signature flaw of this codebase is a complete
absence of authentication and ownership checks (C012, C009). DELETE /items/{id}
acts on any item for any caller. Chained with GET /items enumeration, a single
anonymous script can wipe the entire marketplace — a direct consequence of this
app's specific design, not a library CVE.

## Method
To avoid destroying real data in the demo, the script creates two throwaway
items, then deletes them as an anonymous caller (no credentials). The same
DELETE works on any id, so looping over all enumerated ids (C019 showed 25/25
reachable) would destroy the full catalogue.

## Result
    created throwaway victim items: [29, 30]
    deleted item 29 -> HTTP 200
    deleted item 30 -> HTTP 200

Both deletions succeeded with no credentials and no ownership check.

## Impact
Critical in effect: total, irreversible destruction of all marketplace listings
by any anonymous user. No account, no authorisation, no audit trail.

## Remediation
Require authentication on DELETE (and all state-changing routes), add an
ownership check, and log deletions. See C012 / C026.