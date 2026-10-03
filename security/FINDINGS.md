# CS Track — Findings Log

## Threat modelling (Phase 1)
| ID | Task | Status | Evidence |
|----|------|--------|----------|
| C001 | Architecture + trust boundaries | done | C001-architecture.md + .png |
| C002 | Endpoint inventory | done | C002-endpoint-inventory.md |
| C003 | STRIDE analysis | done | C003-stride.md |
| C004 | Attack surface mapping | done | C004-attack-surface.md |
| C005 | Attack tree | done | C005-attack-tree.md |
| C006 | Threat assessment (top 5) | done | C006-threat-assessment.md |

## Findings (Phase 2 — code review)
| ID | Finding | CWE | Severity | Status | Evidence |
|----|---------|-----|----------|--------|----------|
| C007 | SQLi in /items/search | 89 | Critical | done | C007 report + c007_sqli_poc.py |
| C008 | Stored XSS in /admin | 79 | High | done | C008 report + screenshots |
| C009 | IDOR on DELETE/PATCH | 639 | High | done | C009 report + c009_idor_poc.txt |
| C010 | Hardcoded secret key | 798 | Medium | done | C010 report |
| C011 | Plaintext passwords | 328 | High | done | C011 report |
| C012 | Missing authentication | 306 | High | done | C012 report + delete PoC |
| C013 | Overly permissive CORS | 942 | Medium | done | C013 report |
| C014 | Version info exposure | 200 | Low | done | C014 report + header PoC |
| C015 | Error handling review | 209 | Info | done | C015 report (no leak found) |
| C016 | Audit of SE teammates' fixes | — | Review | done | C016 report (3 bug reports) |

## Security testing (Phase 3 — exploits)
| ID | Task | Status | Evidence |
|----|------|--------|----------|
| C017 | SQLi exploit script | done | c007_sqli_poc.py + C017 report |
| C018 | XSS exploit (3 payloads) | done | c018_xss_payloads.py + screenshot |
| C019 | IDOR enumeration script | done | c019_idor_enum.py + screenshot (25/25) |
| C020 | Rate limit / DoS test | done | c020_rate_limit.py + screenshot |
| C021 | Automated scan (nmap + Python) | done | c021_scan.py + screenshot |
| C022 | API fuzzer | done | c022_fuzzer.py + poc (unbounded price) |
| C023 | Project-specific exploit | done | c023_mass_delete.py + screenshot |
| C024 | test_security.py (8+ cases) | done | test_security.py — 6 pass, 3 fail |

## Deployment & hardening (Phase 4)
| ID | Task | Status | Evidence |
|----|------|--------|----------|
| C025 | Fix SQL injection | todo | — |
| C026 | Add authentication + fix IDOR | todo | — |
| C027 | Secure configuration | todo | — |
| C028 | Security headers + rate limiting | todo | — |
| C029 | Structured logging + alerting | todo | — |
| C030 | Final audit report | todo | — |