# v0.6.6.2 — Diadora S3S Existing Product Discovery Test

GET-only test product:
Diadora Utility GLOVE A.BOX LOW PRO S3S, item 701.183119_80013.

The test adds conservative model-family containment so descriptive store
prefixes such as "Работни обувки Diadora" do not hide an existing product.

S1PS and S3S remain distinct identities.

Expected mela99.com outcome:
EXISTING if exact identifier evidence is found, otherwise POSSIBLE_DUPLICATE
when the same S3S model family is found. NEW is treated as a test failure
because a known public mela99.com page exists.

No website write. No Dolibarr write. No supplier write.
