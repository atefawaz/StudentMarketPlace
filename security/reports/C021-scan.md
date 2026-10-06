# C021 — Automated Scan (nmap + Python)

Automated reconnaissance: an nmap service scan plus a Python endpoint sweep.

Script: security/exploits/c021_scan.py
Evidence: C021-scan.png

## Method
1. nmap -sV against port 5000 to identify the service and version.
2. A Python loop that requests each known endpoint and records the HTTP status,
   mapping the attack surface automatically (including the undocumented routes
   found in C002).

## Result
Port scan:
    5000/tcp open http Uvicorn

Endpoint sweep:
    GET  /items               -> 200
    GET  /items/1             -> 200
    GET  /items/search?q=test -> 400   (shadowed by /items/{item_id})
    GET  /admin               -> 200   (undocumented, no auth)
    GET  /categories          -> 200
    POST /items               -> 400   (exists; empty body rejected)
    PATCH /items/1            -> 400   (exists; empty body rejected)
    DELETE /items/99999       -> 200   (reachable, no auth)
    POST /sellers/register    -> 400   (exists; empty body rejected)
    GET  /nonexistent         -> 404

## Findings
- Service/version disclosure: nmap fingerprints the server as Uvicorn.
- All undocumented endpoints (/admin, PATCH, DELETE, /sellers/register,
  /categories) are confirmed reachable, backing the C002 inventory with
  tool-driven evidence.
- DELETE /items/{id} returns 200 even for a non-existent id and requires no
  auth — reachable to any anonymous caller (ties to C012).
- /items/search returns 400 due to route shadowing by /items/{item_id}
  (see C007).

## Remediation
Minimise service banners where possible; the substantive issues are the
missing authentication (C012) and route shadowing (C007), tracked separately.