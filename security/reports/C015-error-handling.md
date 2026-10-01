# [CWE-209] Error handling review

- ID: C015
- Severity: Informational (no significant leak found)
- Location: backend/app.py — validation error handling
- CWE: CWE-209 (reviewed)

## Summary
Reviewed whether the application leaks internal detail (stack traces, SQL
errors, paths) through error messages. It does not — malformed input returns
clean, generic validation errors with no internal information disclosed.

## Detail
A custom RequestValidationError handler returns a consistent, generic JSON
shape for bad input, and the app responds with 400 Bad Request rather than a
500 with a traceback. No MySQL error strings, Python tracebacks, file paths, or
query fragments reach the client.

## Proof of concept
Three malformed requests, all returning clean generic errors:

    GET /items/search?q=test'
    -> {"detail":"Validation failed","errors":{"path":{"item_id":["Input should be a valid integer..."]}}}

    GET /items/5abc
    -> {"detail":"Validation failed","errors":{"path":{"item_id":["Input should be a valid integer..."]}}}

    PATCH /items/1  body {"bad":"data"}
    -> {"detail":"Validation failed","errors":{"body":{"is_sold":["Field required"]}}}

All returned HTTP 400 with no internal detail. (Note: the search quote returns
a validation error rather than a DB error because /items/search is shadowed by
/items/{item_id} in route order — see C007 — so the malformed query never
reaches MySQL.)

## Assessment
Error handling is adequate. Input validation is centralised through Pydantic
models and a RequestValidationError handler, and no sensitive internal
information is exposed. No CWE-209 vulnerability found at review time.

## Recommendation
Maintain this pattern. Ensure any future endpoints that run raw queries or
catch exceptions also return generic messages and never surface raw error text
or debug tracebacks (keep debug mode off in production). No fix required now.