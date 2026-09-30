# [CWE-306] Missing authentication on state-changing endpoints

- ID: C012
- Severity: High
- Location: backend/app.py — delete_item(), update_item(), admin_page()
- CWE: CWE-306

## Summary
DELETE /items/{id}, PATCH /items/{id} and GET /admin have no authentication or
authorisation. Anyone who can reach the server can delete or modify any item,
or view the admin panel.

## Detail
None of these routes check who is calling. There is no login, token, session,
or ownership check anywhere:

    @app.delete("/items/{item_id}")
    def delete_item(item_id: int):
        ...deletes any item by id...

    @app.patch("/items/{item_id}")
    def update_item(item_id: int, request_body: dict):
        ...updates any item by id...

    @app.get("/admin", response_class=HTMLResponse)
    def admin_page():
        ...returns the admin panel to anyone...

Because there is no concept of "who owns this item", any caller can act on any
item — this is also an IDOR (see C009).

## Proof of concept
Deleting an item with no credentials of any kind:

    curl -X DELETE http://localhost:5000/items/22
    -> {"message":"Item deleted"}

No login, token, or ownership check was required — the item was destroyed.
An earlier DELETE against item 23 (which we neither created nor owned) also
succeeded, confirming any item can be deleted by anyone.

## Impact
High. An attacker can wipe or tamper with every listing and read the admin
page, with no account and no barrier. Combined with the /admin XSS (C008) and
the unauth DELETE, an attacker can fully manipulate the marketplace's data.

## Remediation
Require authentication on all state-changing routes and the admin page, and add
an ownership check so a user can only modify their own items. See C026.