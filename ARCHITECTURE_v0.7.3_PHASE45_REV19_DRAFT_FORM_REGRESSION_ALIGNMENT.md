# M99 v0.7.3 Phase 4.5 Revision 19 — Draft Form Fix + Regression Contract Alignment

Revision 18 fixed the live DRAFT submit defect by removing invalid nested HTML
forms, but full regression rolled back because an older Rev13 test still
expected the obsolete direct manufacturer POST form inside Supplier Browser.

Revision 19 keeps the correct form separation:
Supplier Browser -> GET /supplier-browser/manufacturer-start
-> separate manufacturer page
-> POST /supplier-browser/manufacturer-review

DRAFT remains one valid form:
selected_url + target -> POST /supplier-browser/create-job

The old Rev13 regression test is aligned to this newer contract.
