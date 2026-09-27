# M99 UNO LOW Channel Preflight v1

Windows-accepted parent: `66c0910a1595484bbbb00259246c7cc520329446`.

Purpose: preflight all currently authorized + registry-READY product channels for Panda UNO LOW 11720E without publishing.

Rules:
- `WRITE_TARGETS = REQUESTED ∩ AUTHORIZED ∩ READY`.
- Public network probe is HTTPS **GET only**.
- Credentials are checked only by environment-variable presence and are never printed.
- No product POST/PUT/PATCH/DELETE.
- No website write, DB migration, process kill, commit or push.
- `alviro.ro`, `toplinka.com`, and `dolibarr` remain blocked by registry policy.
- Channel language mapping is explicit; IDs are not guessed.
- Price margin is stable pseudo-random 1.00–1.70%, keyed by product identity + verified supplier gross, so it remains stable until supplier gross changes.
- Operator write approval remains false.

A public HTTPS PASS is reachability evidence only; it is not API-write authorization.
