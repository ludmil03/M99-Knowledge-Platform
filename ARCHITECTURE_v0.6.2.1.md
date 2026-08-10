# M99 Knowledge Platform v0.6.2.1
## Identity & Review Scope Fix

This hotfix corrects four v0.6.2 issues.

1. Preview schema is now `0.6.2.1`.

2. M99 identity uses one numeric namespace:
   - ProductGroup: `M99 100002`
   - size 35 variant: `M99 100003`
   - ...
   - size 48 variant: `M99 100016`

   Every variant stores `parent_m99_id = M99 100002`.
   No hyphenated M99 variant identifiers are allowed.

3. Supplier mapping review is scoped separately from product identity.
   For the Diadora exact manufacturer item:
   - product identity = VERIFIED
   - manufacturer content = VERIFIED
   - supplier mapping = REVIEW
   - pricing = BLOCKED
   - supplier availability = BLOCKED
   - publication = REVIEW

   Supplier conflicts do not invalidate the verified manufacturer product.

4. Commercial values from a near-match supplier record are quarantined.
   The Stenso S3S candidate price and size availability cannot be used for
   the Diadora S1PS item until exact supplier identity is established.

Existing Product Discovery is now explicitly required before first publish.

## Updater safety
v0.6.2.1 is a minimal patch payload. It does not include or overwrite
`integrations/bultex_b2b/__init__.py`, preventing the repeated unwanted local
change seen in previous v0.6.x installers.
