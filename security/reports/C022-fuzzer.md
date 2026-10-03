# C022 — API Fuzzer

Fuzzes the API with malformed, oversized, and wrong-type inputs to find
unhandled edge cases (500 errors) and validation gaps.

Script: security/exploits/c022_fuzzer.py

## Method
Ten hostile input values (empty, 10KB string, SQL metacharacters, XSS, path
traversal, null byte, huge number, etc.) are sent to:
- GET /items/search (the q parameter)
- POST /items (the price field)
- POST /items (completely malformed bodies: non-JSON, wrong types, empty array)

Anything returning HTTP 500 is flagged as an unhandled error.

## Result
0 server errors. Every injection, oversized, null-byte, path-traversal and
wrong-type input returned a clean 400 (rejected). Input validation is robust.

One anomaly:

    POST /items price='99999999999999999999' -> 201 Created

A 20-digit price was accepted and the item created.

## Findings
- Validation is strong: no 500s; all malformed/malicious inputs rejected with
  400. The Pydantic models and the RequestValidationError handler (see C015)
  handle hostile input cleanly.
- Validation gap: price has no upper bound. The model enforces price > 0 but no
  maximum, so absurd or potentially overflowing values are accepted. Low
  severity, but could cause display issues or downstream numeric overflow.

## Remediation
Add an upper bound to the price field in the ItemCreate model, e.g.
    price: float = Field(..., gt=0, le=1_000_000)
No action needed on the rest — validation handled all other fuzz inputs.