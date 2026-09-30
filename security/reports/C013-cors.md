# [CWE-942] Overly permissive CORS configuration

- ID: C013
- Severity: Medium
- Location: backend/app.py — CORSMiddleware setup
- CWE: CWE-942

## Summary
CORS is configured to allow any origin while also allowing credentials. This
combination lets any website make authenticated cross-origin requests to the
API on behalf of a logged-in user.

## Detail
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

allow_origins=["*"] means every website is trusted. allow_credentials=True
means the browser will send cookies/auth with cross-origin requests. Together
these are unsafe: any malicious site a logged-in user visits could call this
API with the user's credentials. (The spec disallows `*` with credentials, but
relying on that is not a fix.)

## Impact
Medium. Once authentication exists, this enables cross-site request abuse —
a third-party page acting as the logged-in user against this API.

## Remediation
Replace the wildcard with an explicit allowlist of the app's real origins
(the actual frontend URLs), and only enable credentials for those. Do not
combine allow_origins=["*"] with allow_credentials=True. See C028.