# M99 Knowledge Platform v0.6.0
## Multi-Channel Product Acquisition Pipeline

Canonical flow:

Manufacturer → Supplier Offer → M99 ProductGroup → ProductVariant → Dolibarr → Channel Assignment → Channel Content/SEO/Price → Publication

### Binding rules
- M99 is the canonical product identity.
- Human-readable M99 IDs use `M99 ` followed by digits.
- Existing MoneyWork, supplier, Dolibarr and website identifiers remain mappings and are preserved.
- ProductGroup lifecycle: `draft → active → paused → retired`.
- Deletion is exceptional and requires operator approval plus literal `DELETE`.
- Size/color/width/etc. are variants of one product model, not independent ProductGroups.
- Existing website URLs are protected.
- Existing SEO/content is replaced only when evidence shows the new version is better.
- New ProductGroup first publication requires operator approval.
- Supplier offers are separate from product identity and may coexist for multiple suppliers.
- Stenso target price: 1.5% below Stenso public price, never below the configured acquisition floor.
- Supplier availability may feed sellable availability; ownership rules remain separated from channel content.
- Dolibarr remains the operational stock/ERP target; M99 remains the product/knowledge master.

### Channel scope
- mela99.com: workwear, safety, medical, HORECA, hotel, restaurant, SPA/wellness, beauty and related professional categories.
- m99.eu: same broad professional scope.
- rabotni-drehi.com: workwear/safety plus medical clothing, clogs/shoes, HORECA, hotel, restaurant, SPA/wellness and beauty.
- medicinski-drehi.com: medical products only.
- laviro.ro: broad professional scope including medical and HORECA.
- alviro.ro: medical plus HORECA/hotel/restaurant/SPA/beauty; industrial-only products are excluded.

### Content
Each channel owns its own language, title, description, H1/H2/H3, metadata, FAQ, image ALT text and category mapping. Content is not copied blindly between sites.
