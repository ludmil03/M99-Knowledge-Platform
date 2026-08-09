import json
import os

from integrations.bultex_b2b.login_diagnostics import (
    diagnose_login_page,
    diagnostics_as_dict,
)


print("Bultex99 B2B LOGIN PAGE DIAGNOSTICS")
print("===================================")
print("Mode: READ-ONLY / NO LOGIN ATTEMPT")
print()

# Optional hint preserves the portal URL shape if available.
# It is never printed and never persisted.
hint = os.getenv("BULTEX_B2B_CLIENT_CODE_HINT", "").strip() or None

diag = diagnose_login_page(client_code_hint=hint)
data = diagnostics_as_dict(diag)

print("HTTP status:", data["status_code"])
print("Final URL:", data["final_url"])
print("Query parameter names:", data["query_parameter_names"] or "(none)")
print("Password keyword present:", data["password_keyword_present"])
print("Login keyword present:", data["login_keyword_present"])
print()

print("FORMS")
print("-----")
if not data["forms"]:
    print("(no <form> blocks found)")
else:
    for form in data["forms"]:
        print(f'Form #{form["index"]}')
        print("  action:", form["action"] or "(empty)")
        print("  method:", form["method"])
        print("  onsubmit:", form["onsubmit"] or "(none)")
        print("  inputs:")
        if not form["inputs"]:
            print("    (none)")
        for field in form["inputs"]:
            print(
                "   - name="
                + str(field["name"])
                + " type="
                + field["input_type"]
                + " has_value="
                + str(field["has_value"])
                + " value=<redacted>"
            )
        print()

print("SCRIPT SOURCES")
print("--------------")
for src in data["script_sources"]:
    print(" -", src)
if not data["script_sources"]:
    print("(none)")
print()

print("INLINE FUNCTION NAMES")
print("---------------------")
for name in data["inline_function_names"]:
    print(" -", name)
if not data["inline_function_names"]:
    print("(none)")
print()

print("Diagnostics completed.")
print("No credentials were submitted.")
print("No login was attempted.")
print("No cookies, session IDs or input values were printed.")
