from dataclasses import dataclass
from decimal import Decimal
from typing import Optional

@dataclass
class SupplierWarehouseStock:
    warehouse_code: str
    warehouse_name: str
    quantity: Decimal

@dataclass
class SupplierOffer:
    supplier: str
    supplier_product_id: str
    supplier_variant_code: str
    name: str
    size: Optional[str]
    barcode: Optional[str]
    currency: str
    purchase_price_ex_vat: Decimal
    recommended_price_ex_vat: Decimal
    warehouse_stock: SupplierWarehouseStock
    source_url: str
