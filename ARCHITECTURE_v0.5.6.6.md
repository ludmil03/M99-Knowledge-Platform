# v0.5.6.6 — Bultex Authentication Response Diagnostics

This build diagnoses why the real portal returns the login page after the native
GET login request. It reports parameter names, status/final path, login-page
detection, short visible status messages, form names and cookie names only.
Credential values, query values and cookie/session values are never printed.
Client code and username are trimmed before submission.
