# M99 v0.7.3 Phase 4.5 Revision 13 — Multi-Source Manufacturer Enrichment

## New rule
A supplier product may have one or more evidence sources.

For the current vertical slice:
- SUPPLIER source: STENSO
- MANUFACTURER source: PANDA SAFETY

The operator can add an official manufacturer product URL from the Supplier Browser.

## Source authority
SUPPLIER:
- current price
- current supplier availability
- current supplier size/variant availability
- supplier article/reference

MANUFACTURER:
- official model
- manufacturer code
- EN/ISO standard
- protection category
- official technical specifications/materials
- technical data sheet
- preferred official images

M99:
- canonical identity
- generated/reviewed descriptions
- localized SEO
- governance
- channel mappings

## Identity
Supplier reference and manufacturer code are separate identifiers.
They must never overwrite each other.

Cross-source match is evidence-based and requires operator confirmation.
Model-name matching can yield PROBABLE_MATCH but never automatic final identity.

## Current gate
This revision validates live multi-source hydration and comparison.
DRAFT is deliberately blocked on the manufacturer comparison screen until
persistent source-evidence confirmation is implemented and tested.
