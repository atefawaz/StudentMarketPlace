# [CWE-89] SQL Injection in item search

- ID: C007
- Severity: Critical
- Location: backend/app.py — search_items(), the LIKE query
- CWE: CWE-89

## Summary
The search query builds SQL by inserting the user's `q` parameter directly
into the statement with an f-string, so a crafted `q` can rewrite the query
and read data from other tables, including seller credentials.

## Detail
The vulnerable line:

    sql = f"SELECT * FROM items WHERE title LIKE '%{q}%' OR description LIKE '%{q}%' ORDER BY created_at DESC"

`q` is concatenated into the SQL text with no parameterisation, unlike every
other query in the codebase (which use %s placeholders). A `q` value
containing a quote closes the string literal and lets the attacker append
their own SQL.

Reachability note: the /items/search route is currently shadowed by
/items/{item_id} (declared above it), so the endpoint returns a 422 int-parse
error over HTTP. The openapi schema confirms all three routes are registered.
The SQLi is therefore latent over HTTP but becomes fully exploitable the
moment the route order is corrected (which the SE team will do to make search
work). This PoC exercises the exact vulnerable query against the same database
to demonstrate the flaw independently of the routing bug.

## Proof of concept
Script: security/exploits/c007_sqli_poc.py

Output:

    2 items for 'book'
    20 items for OR 1=1
    admin admin123 None
    alice_martin password None
    lucas_dupont lucas2026 None

- Baseline "book" search: 2 items.
- Payload `%' OR '1'='1`: returns all 20 items — WHERE clause overridden.
- Payload `x' UNION SELECT ... FROM sellers -- `: extracts seller usernames
  and passwords, including admin / admin123.

## Impact
Full read access to the database via the search endpoint, including the
sellers table where passwords are stored in plaintext (see C011). An attacker
recovers the admin credentials, enabling account takeover once any
authentication is added.

## Remediation
Use parameterised queries (%s placeholders) as the rest of the codebase does.
See C025 for the fix.