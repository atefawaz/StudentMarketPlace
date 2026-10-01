# [CWE-639] Insecure Direct Object Reference (IDOR)

- ID: C009
- Severity: High
- Location: backend/app.py — delete_item(), update_item_sold()
- CWE: CWE-639

## Summary
DELETE /items/{id} and PATCH /items/{id} act on any item by its id with no
check that the caller owns it. Any user can delete any listing, or flip any
listing's sold status, by changing the id.

## Detail
Verified against current code (the endpoints have changed since the initial
audit — PATCH has been parameterised and now uses a validated model, closing
the earlier injection issues, but neither endpoint added an ownership check).

DELETE — no auth, no ownership check:

    def delete_item(item_id: int):
        cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))

PATCH — now parameterised and validated (injection fixed), but still no
ownership check:

    def update_item_sold(item_id: int, payload: ItemSoldUpdate):
        cursor.execute("UPDATE items SET is_sold = %s WHERE id = %s",
                       (payload.is_sold, item_id))

Nothing compares the item's seller to the caller on either endpoint. This is
distinct from missing authentication (C012): even once login exists, without an
ownership check any user could still act on items that are not theirs.

## Proof of concept
Deleted an item owned by another seller, as an unrelated caller with no
credentials:

    POST /items {"seller_name":"victimuser", ...}  -> item created, id 20
    DELETE /items/20                               -> {"message":"Item deleted"}

The item was destroyed by a caller who did not own it. PATCH exhibits the same
missing ownership check for the is_sold field.

## Impact
High. Any user can delete every other user's listings by iterating ids, and
flip any listing's sold status. Combined with no authentication (C012), this is
unrestricted control over listing data.

## Remediation
Add an ownership check on both endpoints: resolve the item, confirm its seller
matches the authenticated user, reject with 403 otherwise. Requires
authentication to exist first. See C026.