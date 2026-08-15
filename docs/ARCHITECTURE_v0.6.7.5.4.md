# M99 v0.6.7.5.4 — Content Engine Restore + Local Credential Bridge

## Fixed blocker 1 — tested Cherokee content engine

The exact v0.6.7.4.2 Cherokee full-content engine is restored unchanged, with
compatibility aliases only. The previously observed content QA remains the basis:
multilingual BG/EN/RU/RO, six content sections, FAQ, ALT data and provenance.

## Fixed blocker 2 — credentials

Credentials are entered once through `SETUP_V06754_LOCAL_CREDENTIALS.bat`.

They are stored outside the Git repository under the current Windows profile and
encrypted with Windows DPAPI. The encrypted values are bound to the current
Windows user profile. The bridge decrypts them only into the process environment
for the preflight/write-gate process and clears those process variables afterwards.

No secret is printed or committed.

## New GET-only readiness

After credentials exist, preflight authenticates against all five real target
channels and discovers API/product-route readiness. For PrestaShop-family
channels it also reads the available currencies.

This is intentionally reviewed before the first real write because the default
currency of every Romanian channel has not yet been proven. The system must not
blindly write numeric `48.65` into a RON channel.

## m99.eu

`m99.eu` remains TASK_ONLY and receives no product write.
