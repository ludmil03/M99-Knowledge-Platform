# v0.5.6.4 — Bultex Login JavaScript Discovery

The portal login diagnostics established:
- form method = GET
- action = /pap/login.php
- CNum is a named field
- username/password field names are dynamically generated
- both are type=text
- onsubmit = checkit()

This release inspects the login JavaScript only.
It reports ordered field names, visible labels, the checkit() function body,
referenced login field names and helper scripts checked.

No credentials are requested and no login is attempted.
