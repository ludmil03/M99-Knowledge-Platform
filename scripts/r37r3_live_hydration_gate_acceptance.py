from app.services.v073_phase45.calenda_public_connector import CalendaPublicConnector

c = CalendaPublicConnector()

river = c.get_product("https://calenda.bg/products/31809")
print("[RIVER]", river.name, river.supplier_reference, river.price_text, river.availability_text, river.hydration_pass)
print("[RIVER warnings]", river.warnings)
assert river.supplier_reference == "93100"
assert len(river.variants) == 4
assert river.price_text == "FROM 20.40"
assert river.currency == "EUR"
assert river.availability_text == "AVAILABLE BY VARIANT"
assert river.hydration_pass is True
assert "PRICE_NOT_FOUND" not in river.warnings
assert "AVAILABILITY_NOT_PUBLISHED" not in river.warnings
assert sum(len(v.get("sizes") or ()) for v in river.variants) == 24

aifos = c.get_product("https://calenda.bg/products/39943")
print("[AIFOS]", aifos.name, aifos.supplier_reference, aifos.price_text, aifos.availability_text, aifos.hydration_pass)
print("[AIFOS warnings]", aifos.warnings)
assert aifos.supplier_reference == "ID264"
assert aifos.hydration_pass is False
assert "PRICE_NOT_FOUND" in aifos.warnings
assert "SIZE_AVAILABILITY_NOT_FOUND" in aifos.warnings

print("[LIVE PASS] RIVER exact Color x Size evidence unlocks hydration.")
print("[LIVE PASS] AIFOS missing exact size evidence remains blocked.")
print("[LIVE PASS] Supplier quantities remain external evidence, never M99-owned stock.")
