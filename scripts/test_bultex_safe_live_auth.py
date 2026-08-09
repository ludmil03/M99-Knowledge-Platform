from decimal import Decimal

from integrations.bultex_b2b.safe_live_auth import BultexSafeReadOnlyClient

PRODUCT_ID = "109168"
WAREHOUSE_CODE = "222"
WAREHOUSE_NAME = "Радиново - Логистична база Радиново"

PREVIOUS = {
    "supplier_variant_code": "06200368.39",
    "purchase_price_ex_vat": Decimal("23.24"),
    "recommended_price_ex_vat": Decimal("37.08"),
    "warehouse_quantity": Decimal("45"),
    "barcode": "2006200368030",
}

client = BultexSafeReadOnlyClient()

print("[1/3] Discovering current dynamic login fields...")
client.discover_login_form()
print("      OK")

print("[2/3] Authenticating read-only session...")
auth = client.login()
print("      OK")
print("      Final authenticated path:", auth["final_path"])

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
    "name": offer.name,
}

print("BULTEX LIVE READ RESULT")
print("=======================")
for key, value in actual.items():
    if key in PREVIOUS:
        prev = PREVIOUS[key]
        state = "UNCHANGED" if value == prev else "CHANGED"
        print(f"{key}: {value} [{state}; previous={prev}]")
    else:
        print(f"{key}: {value}")

print()
print("READ-ONLY integration test completed.")
print("No basket, order, Dolibarr or website write was performed.")
