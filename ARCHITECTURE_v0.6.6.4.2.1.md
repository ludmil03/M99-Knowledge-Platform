# M99 Knowledge Platform v0.6.6.4.2.1
## GET Client Helper Fix

Hotfix after the v0.6.6.4.2 GET-only live analysis failed before reading
`/api/languages`.

Root cause:
- `get_resource_xml()` called `_raise_for_response()`;
- the installed `ControlledMela99Publisher` only exposed `_check()`.

Fix:
- add one canonical `_raise_for_response()` helper;
- retain `_check()` as a backward-compatible alias;
- route product GET, generic resource GET, blank-schema GET and controlled
  POST/PUT/rollback response validation through the same helper;
- keep safe HTTP diagnostics with query values excluded from stored URL;
- add regression tests for generic GET success and HTTP failure.

Safety:
- installer performs no website write;
- v0.6.6.4.2 live analysis remains GET-only;
- no WRITE_DRAFT should be run as part of this hotfix test.
