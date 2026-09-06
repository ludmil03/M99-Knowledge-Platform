# Revision 31 Phase 4.3 R3.5.6 — Runtime Sidebar Source Discovery & Exact Menu Fix

R3.5.4 and R3.5.5 proved that guessing the Dashboard menu source from one
template path is unreliable.

R3.5.6 first discovers the actual source of the visible sidebar by scanning
`admin-platform/app` for:
- visible menu labels;
- supplier-browser route symbols;
- import-jobs route symbols;
- navigation/sidebar/menu definitions.

It writes a local diagnostic report:
`M99_REV31_PHASE4_3_R356_SIDEBAR_DISCOVERY.json`

Only if one source can be patched safely does it insert:
`Add Products -> /add-products`

If no exact safe structure is found, it stops without changing the menu source.
No DB migration, supplier write, website write, stock write, commit or push.
