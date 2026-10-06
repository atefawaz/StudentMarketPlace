# Security Audit Report — Student Marketplace
## CS Track, Challenge Week CW01

**Author:** Aaliyah Momodu (CS track)
**Scope:** Python / FastAPI backend of the Student Marketplace application
**Period:** Challenge Week CW01

---

## 1. Executive Summary

This report presents a security audit of the Student Marketplace backend. The
assessment covered threat modelling, manual code review, live exploitation, and
verification of the remediation carried out by the software-engineering team.

The application began the week with several critical and high-severity
vulnerabilities. A SQL injection in the search endpoint allowed full read access
to the database; the admin page was vulnerable to stored cross-site scripting;
seller passwords were stored in plaintext; and none of the state-changing
endpoints required authentication. In combination these meant that an attacker
with no account could extract the administrator's credentials and delete or
modify any listing in the marketplace.

Ten findings were identified and reported over the course of the week. The
majority — including every critical and high-severity issue — have since been
remediated by the SE team and independently re-verified: the SQL injection,
stored XSS, missing authentication and insecure direct object reference,
plaintext password storage, hardcoded secret key, and version-information leak
are all fixed and confirmed. Three items remain outstanding at the time of
writing: an overly permissive CORS configuration, and two hardening tasks
(security headers with rate limiting, and structured logging). Each outstanding
item has been documented and handed to the SE team with specific remediation.

The two most damaging issues — the SQL injection and the plaintext password
storage — combined to allow complete credential compromise from a single
unauthenticated request. Both are now closed.

---

## 2. Methodology

The audit followed four phases, mapped to the CS-track task structure.

**Threat modelling.** The system architecture and trust boundaries were mapped,
an inventory of every endpoint was produced (method, inputs, authentication,
sensitivity), a STRIDE analysis was carried out on the main item flow, the full
attack surface of untrusted inputs was catalogued, an attack tree was drawn, and
the top five risks were ranked in a threat assessment.

**Code review.** The backend source was reviewed manually against the common
vulnerability classes, producing ten findings. The review also covered the SE
team's own fix commits for completeness and correctness.

**Security testing.** Each finding was proven with a working proof-of-concept
exploit. This included a SQL-injection credential-extraction script, XSS payload
testing, an IDOR enumeration script, a rate-limit / denial-of-service test, an
automated scan combining nmap and Python, an API fuzzer, a project-specific
exploit chain, and an automated security test suite.

**Verification.** After the SE team implemented fixes, each finding was re-tested
against the current code to confirm the remediation, and the remaining items
were documented with recommendations.

All testing was conducted against a local instance of the application. No
production systems were involved, and all exploitation was limited to the
project's own test data.

---

## 3. Findings

Severity reflects impact and exploitability at the time of discovery.

| ID | Finding | CWE | Severity | Status |
|------|---------|-----|----------|--------|
| C007 | SQL injection in /items/search | 89 | Critical | Fixed and verified |
| C008 | Stored XSS in /admin | 79 | High | Fixed and verified |
| C009 / C012 | Missing authentication and IDOR | 306 / 639 | High | Fixed and verified |
| C011 | Plaintext password storage | 328 | High | Fixed and verified |
| C010 | Hardcoded weak secret key | 798 | Medium | Fixed and verified |
| C013 | Overly permissive CORS | 942 | Medium | Open |
| C014 | Version information exposure | 200 | Low | Fixed and verified |
| C015 | Error handling | 209 | Informational | Adequate, no action |

### 3.1 SQL injection (C007) — Critical

The search endpoint built its SQL query by inserting the user's search term
directly into the query string, rather than using a parameterised query. A
crafted search term could therefore break out of the intended query and run
arbitrary SQL. We demonstrated this by extracting the entire sellers table —
including the administrator's username and password — through a UNION-based
payload sent to the search endpoint. This was the single most serious finding,
giving complete read access to the database from an unauthenticated request.

### 3.2 Stored XSS (C008) — High

The administrative page rendered item fields into HTML without escaping them. An
item created with a script payload in its title was stored in the database and
executed in the administrator's browser when the admin panel was opened. This was
confirmed with a live alert popup. Because the payload is stored, it would fire
on every visit to the page.

### 3.3 Missing authentication and IDOR (C009 / C012) — High

The DELETE, PATCH, and item-creation endpoints required no authentication, and
there was no check that a caller owned the item they were acting on. An
enumeration script modified all twenty-five items in the catalogue as an
anonymous caller, and a further exploit deleted listings with no credentials at
all. This combination of missing authentication and missing ownership checks
meant any anonymous user had full control over every listing.

### 3.4 Plaintext passwords (C011) — High

Seller passwords were stored in the database without hashing. On its own this is
a serious storage failure; combined with the SQL injection above, it meant every
real password — including the administrator's — was directly readable by an
attacker.

### 3.5 Other findings

A hardcoded, weak secret key was committed in the source (C010). The CORS policy
trusted every origin while also allowing credentials (C013). Every response
advertised the server framework and version through a response header (C014).
Error handling was reviewed and found to be adequate, returning generic messages
without leaking internal detail (C015).

---

## 4. Exploitation Summary

Each finding was supported by a working proof of concept:

- **SQL-injection credential extraction** — a script that pulled seller
  usernames and passwords out of the database through the search endpoint.
- **Cross-site scripting** — three distinct payload styles (a script tag, an
  image error handler, and an SVG load handler) stored and rendered on the admin
  page.
- **IDOR enumeration** — a script showing all twenty-five items were modifiable
  by an unauthenticated caller.
- **Unauthenticated mass deletion** — a project-specific exploit chaining item
  enumeration with the open delete endpoint.
- **Automated scan, API fuzzer, and a security test suite** — a combined
  nmap-and-Python scan of the service, a fuzzer that confirmed the input
  validation was robust apart from an unbounded price field, and an automated
  pytest suite asserting the secure behaviour of each finding.

---

## 5. Remediation and Verification

Each finding was filed as an issue for the SE team. The fixes they implemented
were then re-verified against the running application.

- **SQL injection** — the query was rewritten as a parameterised statement using
  placeholders, and a follow-up removed a redundant format string flagged during
  the review. Verified: the previous injection payloads no longer alter the query
  or return any extra data.
- **Stored XSS** — item fields are now escaped before being written into the
  page. Verified: a freshly submitted script payload is rendered as inert text
  rather than executing.
- **Authentication and IDOR** — a token-based authentication layer now protects
  the create, update, and delete endpoints, and an ownership dependency rejects
  any caller who does not own the item. Verified: those endpoints now reject
  unauthenticated requests, and ownership can no longer be supplied or spoofed by
  the client.
- **Plaintext passwords** — passwords are now hashed with bcrypt, and the seed
  credentials have been moved to environment variables. Verified: the sellers
  table now stores bcrypt hashes rather than readable passwords.
- **Hardcoded secret** — the secret key is now read from the environment.
  Verified.
- **Version header** — the header has been removed. Verified: it no longer
  appears in responses.

### Outstanding items

- **CORS (C013)** — the configuration still allows all origins. This was
  re-tested and confirmed to be live. An explicit origin allowlist has been
  recommended; the mobile clients are unaffected because native applications are
  not subject to CORS.
- **Security headers and rate limiting (C028)** — not yet implemented. Detailed
  remediation, including the exact middleware and rate-limiter configuration, has
  been provided to the SE team.
- **Structured logging (C029)** — not yet implemented. A structured-logging
  configuration and request-logging middleware have been recommended, together
  with logging of authentication events for an audit trail.

---

## 6. Conclusion

The application's security posture at the start of the week was weak. With no
authentication, two injection flaws, and plaintext credentials, an anonymous
attacker could read all data — including administrator credentials — and
manipulate every listing. Through the audit these issues were identified, proven
with working exploits, reported, and, for every critical and high-severity
finding, remediated and re-verified. The security-and-development feedback loop
worked as intended: the findings drove concrete fixes, and re-testing confirmed
them.

Three lower-priority items remain outstanding, each documented with specific
remediation handed to the SE team. The two highest-risk issues — the SQL
injection and the plaintext password storage — are fully closed and verified.

A single root cause runs through most of the findings: the application trusted
untrusted input and failed to verify who was making a request. The remedies
reflect that — parameterised queries and output escaping to keep user input as
data rather than code, authentication with ownership checks to establish
identity, and secure configuration to avoid exposing secrets and internals.