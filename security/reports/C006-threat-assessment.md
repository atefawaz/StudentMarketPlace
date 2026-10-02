# C006 — Threat Assessment (Top 5 Risks)

Risks ranked by impact and likelihood. All five are confirmed findings.

## 1. SQL injection in /items/search — CRITICAL
User input is f-stringed into the query, allowing arbitrary reads. We extracted
the full sellers table including the admin credential. Highest risk: trivial to
exploit, total data exposure. (C007)

## 2. No authentication on state-changing routes — HIGH
DELETE, PATCH and /admin require no login. Any anonymous caller can delete or
modify any listing and view the admin panel. (C012)

## 3. Plaintext password storage — HIGH
Seller passwords are stored unhashed. Any database read (e.g. via the SQLi)
yields every real password, including admin / admin123. Amplifies risk #1. (C011)

## 4. Stored XSS in /admin — HIGH
Item fields are rendered into the admin page unescaped. A stored payload runs
in the admin's browser, enabling session theft or actions as the admin. (C008)

## 5. Hardcoded weak secret key — MEDIUM
A short, guessable SECRET_KEY is committed in source. If wired into session or
token signing, it could be used to forge them. (C010)

## Overall
The app has no authentication layer and two injection flaws, so an anonymous
attacker can read all data (including credentials) and manipulate all listings.
The combination of the search SQLi (#1) and plaintext passwords (#3) is the
most urgent: one request yields full credential compromise. Authentication
(C012) and parameterised queries (C007/C025) are the two fixes that close the
most risk.