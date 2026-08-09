# v0.5.6.5 — Bultex Safe Live Authentication

Login mechanism is now evidence-based from the real portal JavaScript:

- method: GET
- action: `/pap/login.php`
- client field: `CNum`
- username field: dynamically discovered `edaderpu_<hash>`
- password field: dynamically discovered `edaderpp_<hash>`
- submit action: `act=li`
- onsubmit validator: `checkit()`

The client discovers dynamic field names on every login attempt instead of
hard-coding their hashes.

After login, the client is allow-listed to read only:
`/pap/minfo.php?i=<numeric_product_id>`

There are no methods for basket, ordering, documents, Dolibarr writes or
website/channel writes.

Credentials remain process-only and are cleared after the test.
