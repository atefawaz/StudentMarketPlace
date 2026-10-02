# C016 — Audit of SE Teammates' Code

Reviewed the SE team's security fixes (merged via PR #128, feature/fix-security)
against current code and the running server. Three bug reports.

## BR1 — SQLi fix leaves a redundant f-string (reintroduction risk)
Severity: Low (latent)
Location: backend/app.py line 116 — search_items()

The SQL injection fix (commit 090b628) correctly parameterises the query, so the
injection is closed:

    cursor.execute(f"SELECT * FROM items WHERE title LIKE %s OR description LIKE %s ORDER BY created_at DESC", (f"%{q}%", f"%{q}%"))

But the query string is still an f-string with no placeholders in it. The `f` is
pointless now and is a trap: if anyone later interpolates a variable into this
string, SQL injection returns. A correctly fixed query should be a plain string.
Recommend removing the `f` prefix.

## BR2 — CORS marked fixed but not actually changed
Severity: Medium
Location: backend/app.py line 44

PR #128 is labelled as addressing CORS (issue #108), but the code is unchanged:

    allow_origins=["*"],

Verified at runtime: the server returns `access-control-allow-origin: *` for a
request with `Origin: http://evil.example`. So the CORS misconfiguration (C013)
is still live despite being marked fixed. Recommend reopening.

## BR3 — PATCH injection fixed but IDOR remains
Severity: High
Location: backend/app.py — update_item_sold()

The PATCH endpoint was hardened against injection (now uses ItemSoldUpdate and
parameterised SQL) — correct. But no ownership check was added, so the IDOR
(C009) persists: any caller can flip any item's is_sold by id. The fix addressed
the injection half but left the access-control half open. Recommend adding the
ownership check (see C009 / C026).

## Summary
Of the merged fixes, the SQLi (C007) and XSS (C008) fixes are correct and the
version-header fix (C014) is verified. The CORS fix (C013) did not land, and the
PATCH fix left the IDOR open. Two of the fixes are incomplete or ineffective —
which is why re-verification against running code matters.