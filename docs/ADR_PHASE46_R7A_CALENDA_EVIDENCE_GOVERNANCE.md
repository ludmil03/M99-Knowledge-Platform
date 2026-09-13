# ADR Phase 4.6 R7A — Calenda Evidence Governance Foundation

R7A introduces a product-agnostic evidence boundary before canonical identity.

Identifier roles are separated:
- Calenda product ID = supplier-page identifier.
- Supplier reference = supplier-side identifier only.
- Manufacturer base MPN = accepted only after exact manufacturer evidence is operator-confirmed.
- Manufacturer variant SKU = separate future mapping.
- Canonical M99 reference = internal permanent identity.

A colour or size token such as `blue`, `Navy`, or `XL` is never accepted as a supplier/product reference.

Variant image provenance is explicit:
- NO_VARIANT_IMAGE_EVIDENCE
- SUPPLIER_GENERIC_SHARED
- SUPPLIER_VARIANT_CANDIDATE
- SUPPLIER_VARIANT_EXACT

If one image URL is reused across multiple colours, it is classified as generic/shared and never
presented as proven colour-specific evidence.

R7A is intentionally a foundation + diagnostic lab. It does not yet rewrite the live Hydration
route because the accepted repository's exact active extraction implementation must be identified
from the Windows runtime before modifying that boundary.

No DB migration, channel write, stock write, commit or push.
