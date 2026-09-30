# [CWE-79] Stored XSS in the admin page

- ID: C008
- Severity: High
- Location: backend/app.py — admin_page(), the HTML f-string
- CWE: CWE-79

## Summary
The admin page builds its HTML by inserting item fields with an f-string and
no escaping. An item whose title contains a script tag runs in the admin's
browser when the page is opened.

## Detail
The vulnerable line:

    html += f"<div class='item'><h3>{item['title']}</h3><p>{item['description']}</p><span>Seller: {item['seller_name']}</span></div>"

item['title'], item['description'] and item['seller_name'] are written into
the page as-is. Because these come from POST /items (which anyone can call),
a stored payload fires whenever the admin loads /admin. This is stored XSS —
the payload persists in the database and executes on every view.

## Proof of concept
Stored the payload by creating an item:

    curl -s -X POST http://localhost:5000/items \
      -H "Content-Type: application/json" \
      -d '{"title":"<script>alert(1)</script>","description":"xss test","price":1,"category":"Books","seller_name":"tester"}'

Response: item created with id 21, title stored verbatim as
<script>alert(1)</script>.

Loading /admin returns the title unescaped:

    <h3><script>alert(1)</script></h3>

The tag is raw (not &lt;script&gt;), so a browser executes it. [Screenshot of
the alert popup: C008-xss-popup.png]

## Impact
Any attacker can store JavaScript that runs in the admin's browser with the
admin's session. This allows cookie/session theft, actions performed as the
admin (e.g. triggering the unauthenticated DELETE endpoint), or defacing the
panel. High severity because it targets a privileged user.

## Remediation
Escape all item fields before inserting them into HTML (Python's html.escape),
or better, render with an auto-escaping template engine such as Jinja2 instead
of building HTML with f-strings. See C028 for hardening. Fix is output-side
(escape on render), not input filtering.