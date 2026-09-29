# [CWE-328] Passwords stored in plaintext

- ID: C011
- Severity: High
- Location: backend/seed.py — seed_users()
- CWE: CWE-328

## Summary
Seller passwords are stored in the database as cleartext. No hashing
function is used anywhere in the codebase.

## Detail
seed_users() inserts credentials directly:

    sellers = [
        ("admin", "admin123", ...),
        ("alice_martin", "password", ...),
        ("lucas_dupont", "lucas2026", ...),
    ]

The password column holds the raw string — no bcrypt, argon2, or even a
legacy hash. The value written is the value used.

## Proof of concept
Recovered live via the C007 SQLi (security/exploits/c007_sqli_poc.py):

    admin admin123
    alice_martin password
    lucas_dupont lucas2026

The passwords are readable directly from the sellers table.

## Impact
Anyone with read access to the database — including via the C007 injection —
obtains every seller's actual password, including the plaintext admin
credential. Full account compromise once login exists; password reuse can
extend the damage beyond this app.

## Remediation
Hash passwords with a strong adaptive KDF (bcrypt or argon2) before storing,
and compare hashes on login. Never store or log the raw password. See C027.