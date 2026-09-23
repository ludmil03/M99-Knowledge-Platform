from pathlib import Path
import sys
from decimal import Decimal
from types import SimpleNamespace

ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0,str(ADMIN))

from app.services.v073_phase46.legacy_supplier_bridge_r2 import (
    from_legacy_bultex_offer, from_stenso_observation, to_current_draft
)

def test_bultex():
    o=SimpleNamespace(
        supplier="BULTEX99",supplier_product_id="123",supplier_variant_code="06200368.39",
        name="T",size="39",barcode=None,currency="EUR",
        purchase_price_ex_vat=Decimal("20"),recommended_price_ex_vat=Decimal("25"),
        warehouse_stock=SimpleNamespace(quantity=Decimal("7")),source_url="https://x")
    c=from_legacy_bultex_offer(o)
    assert c.supplier_reference=="06200368"
    d=to_current_draft(c,["m99.eu"])
    assert d["writes_performed"] is False
    assert d["ready_for_current_gates"] is True

def test_stenso_stock_not_inferred():
    o={"source_name":"Stenso","source_url":"https://x",
       "identity":{"supplier_reference":"08001931","title":"T"},
       "facts":{"sizes_visible":["S","M"]},
       "commercial_observation":{"raw_price_observations":[{"value":25.2,"currency":"EUR"}]},
       "supplier_images":["https://x/a.jpg"]}
    c=from_stenso_observation(o)
    assert all(v.supplier_stock is None for v in c.variants)
    assert to_current_draft(c,["m99.eu"])["ready_for_current_gates"]

def test_fail_closed():
    o={"source_name":"Stenso","source_url":"x",
       "identity":{"supplier_reference":"1"},"facts":{"sizes_visible":["M"]}}
    d=to_current_draft(from_stenso_observation(o),["m99.eu"])
    assert "SUPPLIER_CURRENCY_MISSING" in d["blockers"]
