# Revision 31 Phase 4.3 — Unified Add Products Workspace

## Fixed operator goal

The central M99 acquisition workflow is:

Approved Source → Browse Site → Categories / Products → Selection → Targets → DRAFT → Hydration / Evidence → Identity → Canonical Preview → Controlled Publish

Operators must be able to:
- add/propose Supplier or Manufacturer sources;
- authorize them through governance;
- browse an approved source without copying URLs as the normal workflow;
- choose exactly one product;
- choose multiple products;
- choose one category;
- choose multiple categories;
- choose all products from an approved source;
- choose target channels later in the flow.

## R1 implementation

R1 introduces one `/add-products` workspace that:
- reads ACTIVE approved suppliers/manufacturers from the Rev31 Source Registry;
- links directly to Add Supplier/Manufacturer and Approval Queue;
- shows approved canonical categories and links to category management;
- performs safe READ-ONLY same-domain generic site discovery from an approved source;
- shows discovered category and product candidates;
- provides all five required selection modes;
- refuses cross-domain selection;
- does not misleadingly report "0 products" as a connector success: if generic discovery cannot recognize the site, it explicitly states that a source-specific connector is required;
- creates a visible selection plan inside the operator workspace.

## R1 safety boundary

R1 does NOT:
- create/update channel products;
- write stock;
- write images;
- activate products;
- migrate DB;
- persist credentials;
- auto-authorize a source;
- pretend a generic crawler is a validated source connector.

The installer performs no external HTTP. Runtime discovery happens only after the operator clicks Browse on an ACTIVE approved source.

## Next bridge after R1 acceptance

Selection Plan → source-specific hydration/connector → Identity Resolver → DRAFT ImportJob → Target Channels → Canonical Preview.

First live publish remains exactly one product until the end-to-end operator path passes acceptance.
