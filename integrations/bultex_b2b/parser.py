from decimal import Decimal
import re
from html import unescape
from .models import SupplierOffer, SupplierWarehouseStock

class BultexB2BParseError(ValueError):
    pass

def _text(html):
    s = re.sub(r"<[^>]+>", " ", html)
    return re.sub(r"\s+", " ", unescape(s)).strip()

def parse_product_page(html, source_url, warehouse_code, warehouse_name):
    text = _text(html)
    pid = re.search(r'name=["\']at["\'][^>]*value=["\'](\d+)["\']', html, re.I)
    code = re.search(r"\b(\d{8}\.\d{2})\b", text)
    # Parse prices by semantic labels, not by arbitrary decimals.
    purchase_match = re.search(r"Цена\s+EUR\s+(\d+\.\d{2})", text, re.I)
    recommended_match = re.search(r"Крайна\s+цена\s+EUR\s+(\d+\.\d{2})", text, re.I)
    prices = []
    if purchase_match and recommended_match:
        prices = [Decimal(purchase_match.group(1)), Decimal(recommended_match.group(1))]
    qty = re.search(r"Количество.*?class=[\"'][^\"']*large b[^\"']*[\"'][^>]*>(\d+)", html, re.I|re.S)
    barcode = re.search(r"Баркод\s+(\d{8,14})", text, re.I)
    name = re.search(r"Име\s+(.+?)\s+Група", text, re.I)

    if not pid or not code or len(prices) < 2 or not qty:
        raise BultexB2BParseError("Required B2B fields missing")

    return SupplierOffer(
        supplier="BULTEX99",
        supplier_product_id=pid.group(1),
        supplier_variant_code=code.group(1),
        name=name.group(1).strip() if name else "",
        size=code.group(1).split(".")[-1],
        barcode=barcode.group(1) if barcode else None,
        currency="EUR",
        purchase_price_ex_vat=prices[0],
        recommended_price_ex_vat=prices[1],
        warehouse_stock=SupplierWarehouseStock(warehouse_code, warehouse_name, Decimal(qty.group(1))),
        source_url=source_url,
    )
