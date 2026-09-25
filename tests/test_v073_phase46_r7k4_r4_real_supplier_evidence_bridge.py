from pathlib import Path
import sys, random
from decimal import Decimal
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.real_supplier_evidence_bridge_r4 import *

def good():
    return {
      "supplier":"Palltex","supplier_reference":"042502","product_name":"Daytona",
      "source_url":"https://palltex.bg/bg/p/daytona/17374","observed_at":"2026-09-17T19:00:00+03:00",
      "price_gross":"30,70","currency":"BGN",
      "variants":[
        {"supplier_variant_code":"042502.S","size":"S","availability":"наличен","price_gross":"30.70","currency":"BGN"},
        {"supplier_variant_code":"042502.M","size":"M","availability":"няма наличност","price_gross":"30.70","currency":"BGN"}],
      "image_urls":["https://palltex.bg/media/daytona-1.jpg","https://palltex.bg/media/daytona-1.jpg",
                    "https://palltex.bg/media/logo.png","https://evil.example/daytona.jpg"]
    }

def test_verified_public_observation_and_image_filter():
    e=from_public_page_observation(good(),"palltex.bg")
    assert e.source_status=="VERIFIED" and e.price_gross=="30.70" and e.currency=="BGN"
    assert e.image_urls==("https://palltex.bg/media/daytona-1.jpg",)
    assert [v.availability for v in e.variants]==["IN_STOCK","OUT_OF_STOCK"]

def test_gate_is_read_only_and_stock_separated():
    g=evidence_gate(from_public_page_observation(good(),"palltex.bg"))
    assert g["supplier_stock_is_m99_physical_stock"] is False
    assert g["source_failure_means_zero_stock"] is False
    assert g["writes_performed"] is False and g["website_write_enabled"] is False
    assert g["network_performed_by_bridge"] is False

def test_wrong_host_and_category_urls_fail_closed():
    for u in ("http://palltex.bg/bg/p/daytona/17374","https://example.com/bg/p/daytona/17374",
              "https://palltex.bg/category/17374","https://palltex.bg/"):
        x=good(); x["source_url"]=u
        assert from_public_page_observation(x,"palltex.bg").source_status=="VERIFICATION_FAILED"

def test_missing_price_currency_variants_fail_closed():
    x=good(); x["price_gross"]=None; x["currency"]=None; x["variants"]=[]
    g=evidence_gate(from_public_page_observation(x,"palltex.bg"))
    assert "SUPPLIER_PRICE_NOT_VERIFIED" in g["blockers"]
    assert "SUPPLIER_CURRENCY_MISSING" in g["blockers"]
    assert "VARIANT_EVIDENCE_MISSING" in g["blockers"]

def test_unknown_availability_is_not_out_of_stock():
    assert normalize_availability("maybe",None)==("UNKNOWN",None)
    assert normalize_availability(None,None)==("UNKNOWN",None)

def test_exact_quantity_is_supplier_evidence_only():
    assert normalize_availability(None,"7")==("IN_STOCK","7")
    assert normalize_availability(None,"0")==("OUT_OF_STOCK","0")

def test_legacy_b2b_net_price_never_silently_becomes_gross():
    o=SimpleNamespace(supplier="BULTEX99",supplier_variant_code="06200368.39",size="39",
      barcode="1234567890123",currency="BGN",purchase_price_ex_vat=Decimal("20"),
      recommended_price_ex_vat=Decimal("25"),warehouse_stock=SimpleNamespace(quantity=Decimal("4")),
      source_url="https://b2b.example/product/109168",name="Shoe")
    e=from_legacy_b2b_offer(o,"2026-09-17T19:00:00+03:00")
    assert e.supplier_reference=="06200368"
    assert e.price_gross is None
    assert "PRICE_GROSS_NOT_VERIFIED" in e.failure_reason
    assert e.variants[0].supplier_quantity=="4"

def test_image_noise_rejected():
    urls=["https://x.bg/a.webp","https://x.bg/logo.jpg","https://x.bg/cart.png",
          "http://x.bg/b.jpg","https://x.bg/a.pdf","https://x.bg/a.webp"]
    assert filter_images(urls,"x.bg")==("https://x.bg/a.webp",)

def test_currency_aliases():
    assert normalize_currency("€")=="EUR"
    assert normalize_currency("лв")=="BGN"
    assert normalize_currency("lei")=="RON"
    assert normalize_currency("USD") is None

def test_negative_and_invalid_prices_fail():
    for p in ("-1","abc","",None):
        x=good(); x["price_gross"]=p
        assert from_public_page_observation(x,"palltex.bg").source_status=="VERIFICATION_FAILED"

def test_1000000_mass_simulations():
    rng=random.Random(99404)
    for i in range(1_000_000):
        q = rng.choice([None,"0","1","7","999"])
        label = rng.choice([None,"наличен","няма наличност","unknown"])
        state, qty = normalize_availability(label,q)
        assert state in {"IN_STOCK","OUT_OF_STOCK","UNKNOWN"}
        if q is not None:
            assert qty==str(Decimal(q))
            assert state==("IN_STOCK" if Decimal(q)>0 else "OUT_OF_STOCK")
        cur=rng.choice(["EUR","€","BGN","лв","RON","lei","USD",None])
        n=normalize_currency(cur)
        assert n in {"EUR","BGN","RON",None}
        # every simulation also checks safety invariants on periodic complete evidence
        if i % 10000 == 0:
            g=evidence_gate(from_public_page_observation(good(),"palltex.bg"))
            assert not g["writes_performed"]
            assert not g["website_write_enabled"]
            assert not g["supplier_stock_is_m99_physical_stock"]
