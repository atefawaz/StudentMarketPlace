# [CWE-489/CWE-200] Version information exposure via response header

- ID: C014
- Severity: Low
- Location: backend/app.py — PoweredByMiddleware
- CWE: CWE-200 (information exposure)

## Summary
Every response includes a hardcoded X-Powered-By header advertising the
framework and Python version, giving an attacker free reconnaissance.

## Detail
    class PoweredByMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request, call_next):
            response = await call_next(request)
            response.headers["X-Powered-By"] = "FastAPI/0.104.1 Python/3.11"
            return response

The header leaks the stack and version numbers on every response. Note the
value is also inaccurate — it's hardcoded to FastAPI/0.104.1 Python/3.11, which
does not match the installed versions (relevant to the CVE audit, CX08): the
real versions must be checked with pip, not trusted from this header.

## Proof of concept
    curl -I http://localhost:5000/items
    -> X-Powered-By: FastAPI/0.104.1 Python/3.11

## Impact
Low on its own, but it helps an attacker fingerprint the stack to look up
known vulnerabilities for those versions.

## Remediation
Remove the X-Powered-By header entirely (delete the middleware). Servers should
not advertise their framework or version. See C028.