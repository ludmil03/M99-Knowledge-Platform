# M99 v0.7.3 — Operator Product Import Wizard Foundation

## Purpose

Implement the first generalized operator-first Add Products workflow without
reopening already-decided architecture and without performing real writes.

## Fixed decisions implemented

- operator-first UX;
- one-decision-per-screen direction;
- Supplier/Manufacturer as approved Organization roles;
- operator may propose new Supplier/Manufacturer, pending Super Admin approval;
- selection supports one/many products and one/many categories;
- all-products and first-N modes exist as workflow concepts;
- one/many authorized targets;
- m99.eu is only one target;
- target scope separates requested/authorized/ready/blocked;
- Identity Before Content;
- no write before identity, preflight, operator confirmation and TEST/Draft stage.

## Foundation scope

Implemented:
1. Choose approved source Organization.
2. Submit Supplier/Manufacturer proposal with PENDING_SUPER_ADMIN_APPROVAL.
3. Choose selection mode.
4. Capture product/category selection.
5. Identity-review gate placeholder.
6. Choose one/many target channels/ERP.
7. Compute requested/authorized/ready/blocked scope.
8. Review screen.
9. Prepare-for-preflight endpoint.
10. Session-backed wizard draft.

Not implemented yet:
- canonical DB persistence for ImportJob;
- live Supplier Browser;
- live source catalogue/product browser;
- Identity Resolver/Matcher execution;
- RBAC-driven live authorization registry;
- per-channel live preflight;
- pricing/content/image/variant preparation;
- product write;
- activation.

## Safety

This release performs NO product write and does not contact business websites.
Its purpose is to establish the correct generalized operator workflow foundation.
