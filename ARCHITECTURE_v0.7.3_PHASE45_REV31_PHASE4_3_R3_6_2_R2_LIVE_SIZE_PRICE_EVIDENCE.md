# R3.6.2R2 — Live Size Price Evidence Fix

Live R3.6.2R1 proved that Calenda size and availability extraction works, but
`price_eur` remained `None` in real HTML.

Root cause:
Calenda's textile size table publishes:
`20.40 &euro; <br/> 39.90 лв.`
rather than the synthetic slash form:
`20.40 € / 39.90 лв.`

R2 changes only the size-table price parser:
- anchor on the explicit EUR amount;
- tolerate BGN on the next normalized HTML line with or without `/`;
- preserve existing product-level price parser semantics;
- require all 24 live Color x Size rows for product 31809 to carry an exact EUR price;
- require standard sizes to be 20.40 EUR and XXXL* to be 21.47 EUR.

Supplier availability remains external evidence and never M99-owned stock.

No Identity/DRAFT activation, DB migration, Dolibarr/site/channel write,
commit or push.
