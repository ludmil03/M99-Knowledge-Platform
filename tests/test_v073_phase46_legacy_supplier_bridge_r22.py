from pathlib import Path
import sys, random
from decimal import Decimal
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.legacy_supplier_bridge_r2 import (
    from_legacy_bultex_offer,from_stenso_observation,to_current_draft,validate_candidate
)

def bultex(code="06200368.39",currency="EUR",stock="7"):
    return SimpleNamespace(
        supplier="BULTEX99",supplier_product_id="123",supplier_variant_code=code,
        name="T",size=code.rsplit(".",1)[-1] if "." in code else None,barcode=None,
        currency=currency,purchase_price_ex_vat=Decimal("20"),
        recommended_price_ex_vat=Decimal("25"),
        warehouse_stock=SimpleNamespace(quantity=Decimal(stock)),source_url="https://x"
    )

def test_bultex_reference_split_and_no_write():
    c=from_legacy_bultex_offer(bultex())
    assert c.supplier_reference=="06200368"
    d=to_current_draft(c,["m99.eu"])
    assert d["writes_performed"] is False and d["ready_for_current_gates"] is True

def test_stenso_visible_size_never_becomes_m99_stock():
    o={"source_name":"Stenso","source_url":"https://x",
       "identity":{"supplier_reference":"08001931","title":"T"},
       "facts":{"sizes_visible":["S","M"]},
       "commercial_observation":{"raw_price_observations":[{"value":25.2,"currency":"EUR"}]},
       "supplier_images":["https://x/a.jpg"]}
    c=from_stenso_observation(o)
    assert all(v.supplier_stock is None for v in c.variants)

def test_missing_currency_fails_closed():
    c=from_legacy_bultex_offer(bultex(currency=""))
    d=to_current_draft(c,["m99.eu"])
    assert d["ready_for_current_gates"] is False
    assert "SUPPLIER_CURRENCY_MISSING" in d["blockers"]

def test_missing_variants_fails_closed():
    o={"source_name":"Stenso","source_url":"x",
       "identity":{"supplier_reference":"1"},"facts":{"sizes_visible":[]},
       "commercial_observation":{"raw_price_observations":[{"value":1,"currency":"EUR"}]}}
    d=to_current_draft(from_stenso_observation(o),["m99.eu"])
    assert "VARIANTS_MISSING" in d["blockers"]

def test_channel_dedupe_preserves_order():
    c=from_legacy_bultex_offer(bultex())
    d=to_current_draft(c,["m99.eu","mela99.com","m99.eu"])
    assert d["channel_targets"]==["m99.eu","mela99.com"]

def test_governance_cannot_be_overridden_by_legacy_offer():
    c=from_legacy_bultex_offer(bultex())
    d=to_current_draft(c,["m99.eu"])
    assert d["current_governance"]["identity_allocation"]=="CURRENT_ONLY"
    assert d["current_governance"]["vat_resolution"]=="CURRENT_CHANNEL_POLICY"
    assert d["current_governance"]["publish_state"]=="HIDDEN_FIRST"

def test_5000_deterministic_candidate_simulations():
    rng=random.Random(990422)
    for _ in range(5000):
        base=str(rng.randint(10000000,99999999))
        size=str(rng.randint(35,50))
        curr=rng.choice(["EUR","BGN","RON"])
        c=from_legacy_bultex_offer(bultex(base+"."+size,curr,str(rng.randint(0,999))))
        d=to_current_draft(c,["m99.eu"])
        assert c.supplier_reference==base
        assert d["ready_for_current_gates"] is True
        assert d["writes_performed"] is False
