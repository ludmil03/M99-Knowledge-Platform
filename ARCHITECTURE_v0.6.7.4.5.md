# v0.6.7.4.5
Single six-site GET-only readiness gate before real publication.

Confirmed platform map:
- mela99.com: Thirty Bees / PrestaShop Webservice family
- m99.eu: WordPress REST
- rabotni-drehi.com: WordPress REST
- medicinski-drehi.com: PrestaShop 1.7.8.11
- laviro.ro: PrestaShop 1.6.1.24
- alviro.ro: Thirty Bees 1.1.x

No credentials are written to disk. No POST/PUT/PATCH/DELETE is performed.
The runner checks API authentication, language/resource discovery, product lookup,
and product schema/route accessibility. ALL_SITES_READY is true only when every
required channel passes.
