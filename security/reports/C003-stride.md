# C003 — STRIDE Analysis

Flow analysed: creating an item (POST /items) and viewing items
(GET /items, GET /admin), plus editing/deleting (PATCH/DELETE).

| Category | Threat on this app | Evidence / link |
|----------|--------------------|-----------------|
| Spoofing | No authentication, so any seller_name can be claimed on POST /items and any caller can act as anyone. There is no identity to verify. | C012 |
| Tampering | PATCH /items/{id} lets any caller overwrite any field of any item, with no schema and no ownership check. | C012, CX03 |
| Repudiation | No real logging or audit trail. /sellers/register only logs a line; there is no record of who created, edited, or deleted an item, so actions can't be traced. | — |
| Information disclosure | The search SQLi reads arbitrary tables, exposing the sellers table and its plaintext passwords. The version header and any verbose errors also leak internals. | C007, C011, C014 |
| Denial of service | GET /items/search runs an unindexed LIKE over title/description; large data or high request volume can degrade it. No rate limiting on any route. | (CX07) |
| Elevation of privilege | /admin and the DELETE/PATCH routes need no auth, so an anonymous user gets admin-level capability (view panel, delete/modify any item). Combined with /admin XSS, an attacker can run code as the admin. | C008, C012 |

## Summary
The dominant weaknesses are the complete absence of authentication (enabling
Spoofing and Elevation of privilege) and the injection flaws (enabling
Information disclosure). Repudiation is wide open due to no audit logging.
Every STRIDE category has at least one concrete, mostly already-proven threat
on this application.