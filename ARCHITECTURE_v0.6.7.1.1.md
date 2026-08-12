# M99 v0.6.7.1.1 — Supplier Product Page Extraction & Evidence Merge

This release advances supplier intelligence from URL discovery to page-level evidence.

For every current Stenso and Palltex candidate it performs GET-only extraction of:
title, supplier reference, price, promo price, currency, stock signal, size options,
description, technical facts and image URLs.

Identity is scored independently:
- EXACT
- VERY_STRONG
- NEAR_MATCH
- REJECT

Commercial data from NEAR_MATCH and REJECT candidates is quarantined.
Price and stock are never merged across suppliers. Manufacturer evidence remains
the authority for canonical product identity. Supplier technical conflicts require
operator review.

No M99 selling price is selected. No channel/Dolibarr/supplier write is permitted.
