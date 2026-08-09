from decimal import Decimal
from integrations.bultex_b2b.live_readonly import BultexReadOnlyClient

PRODUCT_ID = "109168"
WAREHOUSE_CODE = "222"
WAREHOUSE_NAME = "Радиново - Логистична база Радиново"

EXPECTED = {
    "supplier_product_id": "109168",
    "supplier_variant_code": "06200368.39",
    "size": "39",
    "purchase_price_ex_vat": Decimal("23.24"),
    "recommended_price_ex_vat": Decimal("37.08"),
    "warehouse_quantity": Decimal("45"),
    "barcode": "2006200368030",
}

client = BultexReadOnlyClient()

print("[1/3] Discovering login form...")
fields = client.discover_login_form()
print("      OK")

print("[2/3] Authenticating read-only session...")
client.login(fields)
print("      OK")

print("[3/3] Reading control product...")
offer = client.read_product(PRODUCT_ID, WAREHOUSE_CODE, WAREHOUSE_NAME)
print("      OK")
print()

actual = {
    "supplier_product_id": offer.supplier_product_id,
    "supplier_variant_code": offer.supplier_variant_code,
    "size": offer.size,
    "purchase_price_ex_vat": offer.purchase_price_ex_vat,
    "recommended_price_ex_vat": offer.recommended_price_ex_vat,
    "warehouse_quantity": offer.warehouse_stock.quantity,
    "barcode": offer.barcode,
}

print("LIVE READ RESULT")
print("----------------")
for key, value in actual.items():
    expected = EXPECTED[key]
    marker = "OK" if value == expected else "CHANGED"
    print(f"{key}: {value}   [{marker}; previous={expected}]")

print()
print("READ-ONLY test completed.")
print("No Dolibarr, basket, order or website write was performed.")
