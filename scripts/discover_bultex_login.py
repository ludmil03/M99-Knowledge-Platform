from integrations.bultex_b2b.live_readonly import BultexReadOnlyClient

client = BultexReadOnlyClient()
fields = client.discover_login_form()

print("Bultex99 B2B login form discovery")
print("---------------------------------")
print("Action:", fields.action)
print("Method:", fields.method)
print("Client code field:", fields.client_code_field)
print("Username field:", fields.username_field)
print("Password field:", fields.password_field)
print("Hidden/submit fields:", ", ".join(sorted(fields.submit_fields)) or "(none)")
print()
print("No credentials were used. No login was attempted.")
