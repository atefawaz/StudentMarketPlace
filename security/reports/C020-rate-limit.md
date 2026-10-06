# C020 — Rate Limit / DoS Test

Tests whether the API throttles rapid requests.

Script: security/exploits/c020_rate_limit.py
Evidence: C020-rate-limit.png

## Method
Send 100 GET /items requests in a tight loop and record the response codes. A
rate limiter would return HTTP 429 (Too Many Requests) once a threshold is hit.

## Result
    sent 100 requests in 208.42s (0 req/s)
    status codes: {200: 100}
    no 429 responses -> NO rate limiting; every request accepted

## Findings
1. No rate limiting. All 100 requests succeeded (200); none were throttled
   (no 429). An attacker can send unlimited requests — enabling brute-force
   (e.g. against a future login) and simple flooding.
2. Very slow responses. 100 requests took ~208 seconds (~2s each), far slower
   than expected for a local API. The backend opens a new MySQL connection per
   request (get_db() with no pooling), so even modest concurrent load could
   saturate resources. This compounds the DoS risk: the service is both
   unthrottled and slow.

## Impact
Medium. No protection against request floods or credential brute-forcing, and
the per-request connection overhead means relatively little traffic is needed
to degrade the service.

## Remediation
Add rate limiting (e.g. slowapi for FastAPI) with sensible per-IP limits on
public and mutating endpoints. Introduce database connection pooling to remove
the per-request connection overhead. See C028.