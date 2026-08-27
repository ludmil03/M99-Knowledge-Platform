# M99 v0.7.3 Phase 4.5 Revision 18 — Draft Form Integrity Fix

## Real GUI defect
Products and target channel could be selected, but `Create DRAFT Import Job`
did not submit.

## Root cause
The Supplier Browser wrapped selection and DRAFT controls in one HTML form,
while each hydrated product card contained another `<form>` for manufacturer
enrichment. Nested forms are invalid HTML. Browsers repair the DOM by closing
or relocating forms, so the DRAFT submit button was no longer reliably bound
to `/supplier-browser/create-job`.

## Fix
- Supplier Browser has exactly one DRAFT selection form.
- Manufacturer enrichment is moved to a separate GET entry page:
  `/supplier-browser/manufacturer-start`
- That separate page owns the POST form to:
  `/supplier-browser/manufacturer-review`
- No nested forms remain.
- Selection, target choice, and DRAFT submit remain in one valid form.

## Safety
No product/channel write is performed by installer.
DRAFT remains operator initiated.
