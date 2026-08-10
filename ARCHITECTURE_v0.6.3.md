# M99 Knowledge Platform v0.6.3
## Existing Product Discovery + Content/SEO Preview

v0.6.3 adds two gates before any first publish.

### 1. Existing Product Discovery

The system checks channel evidence using exact identity signals:
- manufacturer item;
- EAN when available;
- legacy identifier;
- exact model name.

A public search with no exact result is NOT treated as proof that a product is
absent. It produces:

`NO_PUBLIC_EXACT_MATCH_FOUND_REVIEW_REQUIRED`

and requires operator verification before creation.

If an exact existing product is found, M99 must link to it and preserve:
- existing channel product ID;
- existing URL.

### 2. Channel-specific Content/SEO Preview

For the verified Diadora exact item, v0.6.3 generates review-only content for:
- mela99.com: BG + EN;
- m99.eu: BG + EN;
- rabotni-drehi.com: BG;
- laviro.ro: RO.

Each channel has its own wording while sharing only verified manufacturer facts.

Preview fields:
- SEO title;
- meta description;
- H1;
- short description;
- long description;
- H2 structure;
- FAQ;
- image ALT suggestions.

The unresolved Stenso S3S near-match cannot contribute facts, price, stock or
claims to this content.

### Safety

Publication remains blocked until Existing Product Discovery is operator
verified.

No Dolibarr writes.
No website writes.
No supplier writes.

This updater is a minimal patch and does not overwrite Bultex integration files.
