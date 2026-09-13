# ADR Phase 4.6 R7D — First live canonical pilot on m99.eu

R7D is the first package that deliberately enables a controlled real product create on m99.eu.
The installer itself performs no website write and never changes environment variables.

Live write requires all of: Super Admin, DRAFT, exactly one selected item, requested+authorized m99eu, READY R4→R1 canonical preview, permanent M99 reference, verified Manufacturer MPN, EN/BG/RU canonical documents, image evidence, variant/availability evidence, explicit positive operator price, `M99EU_CANONICAL_PILOT_ENABLED=1`, valid `M99EU_API_KEY`, valid category, and exact confirmation phrase.

The created pilot is inactive, unavailable for order, and visibility=none. Duplicate guard runs on permanent M99 reference; existing products are accepted only if their readback is the exact safe hidden pilot state. Product blank schema is read before POST and only supported fields are emitted. Manufacturer MPN is written only if the PrestaShop product schema exposes `mpn`.

R7D intentionally does not upload images in the first write. Image evidence is still a READY gate. Image upload is separated so a first product-create/readback can be proven independently before adding multipart media writes.

No DB migration, stock write, commit, push, or automatic environment mutation.


## SAFE R2 — monotonic migration of the historical R4 hard lock

The first R7D Windows run proved the incoming R7C baseline (`687 passed`) and the new R7D
dedicated tests (`7 passed`). The only failure was an obsolete historical assertion that still
required the literal preview-only hard-lock text.

SAFE R2 preserves the safety invariant and strengthens it: default state remains locked, and a
network write is eligible only when every server-side live gate is simultaneously true. The
historical regression is migrated to test those stronger semantics rather than the obsolete
literal string. Tests are not skipped, xfailed, or weakened.
