# M99 Knowledge Platform v0.6.1
## Product Acquisition Preview Pipeline

Flow:
Structured Source JSON → validation → M99 ProductGroup draft → variants →
supplier offers → channel eligibility → channel preview → operator review.

This release is PREVIEW_ONLY. It performs no Dolibarr, supplier, or website
writes. Existing channel IDs and URLs are preserved in the preview. All channel
records remain REVIEW with publish_allowed=false until an operator approves
them. Sizes/colors remain variants of one ProductGroup.

The sample fixture is synthetic and exists only for smoke testing; it is not
supplier or manufacturer data.
