# C027 — Secure Configuration (verification)

Secrets, password storage, and version exposure were remediated by SE
(issues #102 passwords, #103 secret key, #109 version header).

## The fixes
1. Passwords (C011): seed_users() hashes with bcrypt (12 rounds) into a
   password_hash column; seed passwords moved to environment variables.
2. Secret key (C010): SECRET_KEY read from the environment via
   get_required_env("SECRET_KEY"); no longer hardcoded. .env is gitignored.
3. Version header (C014): the X-Powered-By middleware was removed.

## Verification
- Passwords: after re-seeding, all 8 sellers store bcrypt hashes ($2b$12$...),
  not plaintext (evidence: C011-fix-verified.png). The earlier C007 SQLi would
  now return hashes, not readable passwords.
- Secret key: the server requires SECRET_KEY in .env to start (fail-loud);
  app.py uses get_required_env.
- Version header: test_no_version_header PASSES; curl -I shows no X-Powered-By.

## Status
Secrets, password storage, and version exposure fixed and verified.