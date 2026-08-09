# v0.5.6.3 — Bultex Login Discovery Diagnostics

The live test reached the real B2B portal but discovery failed because the
portal did not expose a standard `<input type="password">` in the returned HTML.

This release adds a diagnostics-only mode.

## What it does
- GET `/pap/login.php`
- optionally preserves the portal's `CNum` URL shape
- lists form action/method
- lists field names and input types
- reports whether fields have values, but NEVER prints those values
- lists script sources
- lists inline JavaScript function names
- lists query parameter names with values redacted

## What it does NOT do
- no credential submission
- no login attempt
- no cookies/session IDs printed
- no basket/order/document writes
- no Dolibarr writes
- no website writes

Run after installation:

`scripts\RUN_BULTEX_LOGIN_DIAGNOSTICS.bat`

Send only the diagnostic output.
