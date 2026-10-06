# [CWE-798] Hardcoded secrets in source

- ID: C010
- Severity: Medium
- Location: backend/app.py line 17 — SECRET_KEY declaration
- CWE: CWE-798

## Summary
A secret key is written directly in the source code as a weak, guessable
string. It is committed to git and visible to anyone with repo access.

## Detail
At the top of app.py:

    SECRET_KEY = "super-secret-key-123"

Two problems:
1. Hardcoded — the value lives in source control, so it is exposed to every
   person who can read the repository and persists in git history forever. A
   secret should be loaded from an environment variable or untracked config,
   not written in code.
2. Weak — "super-secret-key-123" is short and human-chosen, so it is
   guessable/brute-forceable. A secret key should be long and randomly
   generated (32+ random bytes).

A related exposure: PoweredByMiddleware hardcodes a response header
X-Powered-By: FastAPI/0.104.1 Python/3.11, leaking (fake) version info on
every response (see C014).

## Proof of concept
The value is readable directly in app.py line 17, in plaintext — no
exploitation needed, it is committed source.

grep confirms SECRET_KEY is declared but never referenced anywhere else in the
codebase (only match outside the declaration is the compiled .pyc cache). It
is a latent leak: a hardcoded, weak credential in source control that serves
no current function but demonstrates the insecure pattern.

## Impact
Anyone with read access to the repository obtains the key. If it were used to
sign sessions or tokens, an attacker who knows it could forge them. Even
unused, it demonstrates secrets being committed to source — a practice that
will leak real credentials as the app grows.

## Remediation
Load the secret from an environment variable (os.environ) with no default in
production, generate it randomly (e.g. secrets.token_hex(32)), and ensure any
config file holding it is in .gitignore. Rotate the key once exposed. See C027
for the hardening.