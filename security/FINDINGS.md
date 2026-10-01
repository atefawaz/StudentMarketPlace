# CS Track — Findings Log

## Threat modelling (Phase 1)
| ID | Task | Status | Evidence |
|----|------|--------|----------|
| C001 | Architecture + trust boundaries | done | C001-architecture.md + .png |
| C002 | Endpoint inventory | done | C002-endpoint-inventory.md |
| C003 | STRIDE analysis | in progress | C003-stride.md |
| C004 | Attack surface mapping | done | C004-attack-surface.md |
| C005 |C005-Attack-Tree | Attack tree | Done |C005-attack-tree.md|
| C006 | Threat assessment (top 5) | todo | — |

## Findings (Phase 2 — code review)
| ID | Finding | CWE | Severity | Status | Evidence |
|----|---------|-----|----------|--------|----------|
| C007 | SQLi in /items/search | 89 | Critical | done | C007 report + c007_sqli_poc.py |
| C008 | Stored XSS in /admin | 79 | High | done | C008 report + popup screenshot |
| C010 | Hardcoded secret key | 798 | Medium | done | C010 report |
| C011 | Plaintext passwords | 328 | High | done | C011 report |
| C012 | Missing authentication | 306 | High | done | C012 report + delete PoC |
| C013 | Overly permissive CORS | 942 | Medium | done | C013 report |
| C014 | Version info exposure | 200 | Low | done | C014 report + header PoC |