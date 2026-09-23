from pathlib import Path
import sys, random
from decimal import Decimal
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.legacy_supplier_canonical_r3 import *

def bultex(code="06200368.39",currency="EUR",stock="7"):
    return SimpleNamespace(
        supplier="BULTEX99",supplier_product_id="123",supplier_variant_code=code,
        name="T",size=code.rsplit(".",1)[-1] if "." in code else None,barcode=None,
        currency=currency,purchase_price_ex_vat=Decimal("20"),
        recommended_price_ex_vat=Decimal("25"),
        warehouse_stock=SimpleNamespace(quantity=Decimal(stock)),source_url="https://supplier.example/p/123"
    )

def ctx(**kw):
    d=dict(m99_identity="M99 100018",duplicate_state="EXACT_EXISTING",vat_rule_id="STD",
           verified_supplier_gross="100",supplier_currency="EUR",observed_at="2026-09-17T12:00:00",
           persisted_discount=None,previous_verified_supplier_gross=None,
           rounding_policy_id="EXTERNAL_POLICY",rounded_target_gross="98.50")
    d.update(kw); return CurrentGateContext(**d)

def test_bultex_reference_and_supplier_stock_separation():
    c=from_legacy_bultex_offer(bultex())
    assert c.supplier_reference=="06200368"
    p=build_integration_plan(c,["m99.eu"],ctx(),lambda n:0)
    assert p["stock"]["supplier_availability_is_m99_physical_stock"] is False
    assert p["writes_performed"] is False and p["publish"]["live_write_enabled"] is False

def test_stenso_visible_sizes_never_become_owned_stock():
    o={"source_name":"Stenso","source_url":"https://supplier.example/p/1",
       "identity":{"supplier_reference":"08001931","title":"T"},
       "facts":{"sizes_visible":["S","M"]},
       "commercial_observation":{"raw_price_observations":[{"value":"100","currency":"EUR"}]},
       "supplier_images":["https://supplier.example/a.jpg"]}
    c=from_stenso_observation(o)
    assert len(c.variants)==2 and all(v.supplier_stock is None for v in c.variants)

def test_persisted_discount_is_reused_when_benchmark_unchanged():
    p=build_integration_plan(from_legacy_bultex_offer(bultex()),["m99.eu"],
       ctx(persisted_discount="0.0137",previous_verified_supplier_gross="100"),lambda n:700)
    assert p["pricing"]["discount"]=="0.0137"
    assert p["pricing"]["regenerated"] is False

def test_discount_regenerated_only_on_changed_benchmark():
    p=build_integration_plan(from_legacy_bultex_offer(bultex()),["m99.eu"],
       ctx(persisted_discount="0.0137",previous_verified_supplier_gross="99"),lambda n:700)
    assert p["pricing"]["discount"]=="0.017"
    assert p["pricing"]["regenerated"] is True

def test_discount_bounds_exact():
    c=from_legacy_bultex_offer(bultex())
    assert build_integration_plan(c,["m99.eu"],ctx(),lambda n:0)["pricing"]["discount"]=="0.01"
    assert build_integration_plan(c,["m99.eu"],ctx(),lambda n:n-1)["pricing"]["discount"]=="0.017"

def test_unknown_channel_fails_closed_and_valid_order_is_preserved():
    p=build_integration_plan(from_legacy_bultex_offer(bultex()),
       ["mela99.com","BAD","m99.eu","mela99.com"],ctx(),lambda n:0)
    assert p["channel_targets"]==["mela99.com","m99.eu"]
    assert "UNKNOWN_CHANNEL_TARGET" in p["blockers"]
    assert p["ready_for_hidden_publish_plan"] is False

def test_identity_duplicate_vat_rounding_all_fail_closed():
    c=from_legacy_bultex_offer(bultex())
    p=build_integration_plan(c,["m99.eu"],ctx(m99_identity="M99-100018",
       duplicate_state="AMBIGUOUS",vat_rule_id=None,rounding_policy_id=None,rounded_target_gross=None),lambda n:0)
    for x in ("M99_IDENTITY_INVALID","DUPLICATE_GATE_BLOCKED","VAT_RULE_UNRESOLVED","ROUNDING_POLICY_REQUIRED"):
        assert x in p["blockers"]

def test_supplier_price_failure_never_means_zero_stock():
    p=build_integration_plan(from_legacy_bultex_offer(bultex()),["m99.eu"],
       ctx(verified_supplier_gross=None),lambda n:0)
    assert "SUPPLIER_GROSS_NOT_VERIFIED" in p["blockers"]
    assert p["stock"]["supplier_availability_is_m99_physical_stock"] is False

def test_rounded_target_must_be_positive_and_below_supplier_gross():
    c=from_legacy_bultex_offer(bultex())
    for bad in ("0","100","101","-1"):
        p=build_integration_plan(c,["m99.eu"],ctx(rounded_target_gross=bad),lambda n:0)
        assert "ROUNDED_TARGET_INVALID" in p["blockers"]

def test_all_seven_configured_channels_can_be_selected_without_write():
    c=from_legacy_bultex_offer(bultex())
    p=build_integration_plan(c,list(ALLOWED_CHANNELS),ctx(),lambda n:350)
    assert p["channel_targets"]==list(ALLOWED_CHANNELS)
    assert p["ready_for_hidden_publish_plan"] is True
    assert p["writes_performed"] is False

def test_250000_maxsim_matrix():
    rng=random.Random(990403)
    channels=list(ALLOWED_CHANNELS)
    c0=from_legacy_bultex_offer(bultex())
    for i in range(250000):
        gross=Decimal(rng.randint(1,1000000))/Decimal("100")
        k=rng.randrange(701)
        old=(Decimal(1000+rng.randrange(701))/Decimal(100000))
        unchanged=(i%3==0)
        selected=rng.sample(channels,rng.randint(1,len(channels)))
        C=ctx(
            m99_identity=f"M99 {100018+(i%899981):06d}",
            verified_supplier_gross=str(gross),
            previous_verified_supplier_gross=str(gross if unchanged else gross+1),
            persisted_discount=str(old) if i%2==0 else None,
            supplier_currency=rng.choice(["EUR","BGN","RON"]),
            rounded_target_gross=str(gross-Decimal("0.01")) if gross>Decimal("0.01") else "0.001"
        )
        p=build_integration_plan(c0,selected,C,lambda n,k=k:k)
        d=Decimal(p["pricing"]["discount"])
        assert DISCOUNT_MIN <= d <= DISCOUNT_MAX
        if C.persisted_discount is not None and unchanged:
            assert d==Decimal(C.persisted_discount)
        assert p["writes_performed"] is False
        assert p["publish"]["live_write_enabled"] is False
        assert p["stock"]["supplier_availability_is_m99_physical_stock"] is False
        assert p["channel_targets"]==selected
