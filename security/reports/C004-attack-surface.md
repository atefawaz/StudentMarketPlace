# C004 — Attack Surface Mapping

Every point where untrusted input enters the application, and what guards it.

| Entry point | Untrusted input | Validation | Risk |
|-------------|-----------------|-----------|------|
| GET /items/search | q (query string) | none | SQL injection — q is f-stringed into the query (C007) |
| POST /items | title, description, price, category, seller_name (body) | Pydantic (types, price>0, title length) | stored XSS payload survives into /admin (C008) |
| PATCH /items/{id} | raw JSON body — both values AND keys | none | value: arbitrary field writes; key: SQL injection via column name (CX03) |
| PATCH /items/{id} | item_id (path) | int only | IDOR — edits any item, no ownership check (C009/C012) |
| DELETE /items/{id} | item_id (path) | int only | IDOR — deletes any item, no auth (C009/C012) |
| GET /items/{id} | item_id (path) | int only | low — query is parameterised |
| POST /sellers/register | name, email (body) | none | low — only logged, not stored |
| GET /admin | none directly (renders stored items) | n/a | reflects stored item data into HTML unescaped (C008) |

## Notes
- The PATCH endpoint is the unusual one: its JSON *keys* are untrusted input,
  used directly as SQL column names with no allowlist. Most inputs are values;
  here the key itself is an injection vector.
- POST /items is the only entry point with real input validation.
- No entry point requires authentication, so every one is reachable anonymously.
- Two inputs reach SQL unsafely: the search q (C007) and the PATCH keys (CX03).
- One input reaches HTML unsafely: stored item fields rendered by /admin (C008).