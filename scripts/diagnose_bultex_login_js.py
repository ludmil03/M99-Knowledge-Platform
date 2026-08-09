from integrations.bultex_b2b.login_js_diagnostics import diagnose_login_javascript, diagnostics_as_dict

print("Bultex99 B2B LOGIN JAVASCRIPT DIAGNOSTICS")
print("=========================================")
print("Mode: READ-ONLY / NO LOGIN / NO CREDENTIALS")
print()

d = diagnostics_as_dict(diagnose_login_javascript())

print("Form method:", d["form_method"])
print("Form action:", d["form_action"])
print("Ordered named fields:")
for name in d["ordered_named_fields"]:
    print(" -", name)
print()

print("Visible login-related labels:")
for label in d["visible_labels"]:
    print(" -", label)
if not d["visible_labels"]:
    print(" (none)")
print()

print("Referenced login field names inside checkit():")
for name in d["referenced_field_names"]:
    print(" -", name)
if not d["referenced_field_names"]:
    print(" (none)")
print()

print("checkit() implementation(s):")
if not d["checkit_functions"]:
    print(" (not found)")
else:
    for f in d["checkit_functions"]:
        print()
        print("Origin:", f["origin"])
        print("----------------------------------------")
        print(f["source"])
        print("----------------------------------------")

print()
print("External scripts checked:")
for u in d["script_urls_checked"]:
    print(" -", u)
if not d["script_urls_checked"]:
    print(" (none)")
print()
print("Diagnostics completed. No login was attempted.")
