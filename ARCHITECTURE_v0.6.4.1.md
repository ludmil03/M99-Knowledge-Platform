# M99 Knowledge Platform v0.6.4.1 — Content Quality Refinement

## Scope
Refine v0.6.4 content without enabling publication or changing supplier authentication.

## Claim model
- FACT — direct canonical manufacturer fact.
- DERIVED_SAFE_CLAIM — narrow wording derived from a verified fact, with explicit `derived_from`.
- MARKETING_CLAIM — comparative/performance/superlative language; requires explicit evidence and review.
- UNSUPPORTED_CLAIM — blocked.

## Channel profiles
- mela99.com: authoritative product catalogue; technical + commercial; BG/EN.
- m99.eu: professional/international; stronger technical positioning; BG/EN.
- rabotni-drehi.com: transactional search intent; practical product selection; BG.
- laviro.ro: Romanian transactional search; natural Romanian terminology; RO.

## Dynamic FAQ
FAQ is generated only from available canonical facts. For the Diadora fixture it covers protection class, toe cap, anti-puncture, ESD, outsole markings and EU size range.

## Safety boundaries
- No writes to Dolibarr.
- No writes to websites.
- No supplier writes.
- Existing Product Discovery remains a publication blocker.
- Bultex integration is not modified by this update.
