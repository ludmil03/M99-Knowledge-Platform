# Revision 31 Phase 4.3 R3.5.4 — Real Dashboard Sidebar Integration Fix

## Live acceptance failure
The previous menu patch modified `rev31_governance/base.html`, but the actual
Dashboard shown after login uses another template. Therefore browser acceptance
correctly failed even though the generic template gate passed.

## R3.5.4 rule
The real Dashboard sidebar is identified by the exact collection of live labels:
Dashboard, Products, Product Presence, Suppliers / Browse, Import Jobs,
Daily Existing Product Sync, Users, Roles & Permissions, Languages,
Commerce / VAT, Audit Log.

Only the highest-scoring template matching those labels is patched.

## Result
Under IMPORTS:
- Add Products
- Suppliers / Browse
- Import Jobs

`Add Products` points to `/add-products`.

No login redirect is changed in this revision; Dashboard remains the normal
landing page after authentication. The requirement is easy, visible access from
the primary sidebar.

## Safety
No DB migration.
No supplier write.
No target website/stock write.
No commit/push.
Installer external HTTP: NO.
