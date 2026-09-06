# Revision 31 Phase 4.2 — Operator Selected Single Product → m99.eu

Purpose: prove the real operator path from an existing M99 ImportJobItem to one controlled PrestaShop 9 product write.

## Operator flow
M99 Dashboard / Suppliers → Add 1 product to m99.eu → select exactly one M99 ImportJobItem → enter target category → enter API key → exact confirmation → duplicate guard → POST at most one inactive product → mandatory read-back → local audit.

## Safety contract
- exactly one selected item;
- no batch endpoint;
- product is always `active=0`;
- `available_for_order=0`;
- no stock write;
- no image write;
- target category must be API-readable before POST;
- duplicate reference check before POST;
- API key is never written to audit;
- mandatory read-back validates reference, inactive state and category;
- transport uses the proven `curl.exe --ipv4 --http1.1` path.

## Candidate requirements
The chosen ImportJobItem must expose hydrated evidence sufficient for product title, supplier reference/SKU and positive price.

## Reference note
This first controlled bridge uses deterministic `M99-<digits>` references derived from ImportJobItem ID in a reserved high numeric range. A later canonical identity bridge should replace this provisional derivation with the existing identity registry.

## Not implemented here
Batch publishing, activation, stock, combinations/variants, images, automatic category mapping, final AI content generation, credential persistence, multi-channel publish.
