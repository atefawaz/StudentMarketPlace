# C002 — Endpoint Inventory

Issue: #42

| Method |       Path       | Inputs     | Auth                |Sensitivity |
|--------|------------------|------------|---------------------|------------|
| GET    | /items           | none       | none                | low        |
| GET    | /items/{item_id} | item_id    | none                | low        |
| POST   | /items           | title, description, price, category, seller_name | none | medium |
| GET    | /items/search    | q          | none                | high       |
| GET    | /admin           | none       | none                | high       |
| DELETE | /items/{item_id} | item_id    | none                | high       |
| PATCH  | /items/{item_id} | item_id + raw JSON body | none   | high       |
| POST   | /sellers/register| name, email| none                | low        |

## Notes
- No endpoint requires authentication.
- /items/search puts user input straight into SQL (injectable).
- /admin puts item text into HTML without escaping.
- PATCH uses the JSON keys as column names with no checks.