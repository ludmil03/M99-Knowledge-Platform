from __future__ import annotations

from types import SimpleNamespace
import pytest

from app.services.v073_phase46 import palltex_controlled_publish as r7k
from app.services.v073_phase46.canonical_live_pilot import CanonicalPilotResult


def preview(ref="M99-3", supplier="042554", rows=None):
    rows = rows or [
        {"colour":"Антрацит","size":"XS","availability":"SUPPLIER_VISIBLE"},
        {"colour":"Антрацит","size":"S","availability":"SUPPLIER_VISIBLE"},
    ]
    docs={}
    for code in ("EN","BG","RU"):
        docs[code]={
            "product_name":"DAYTONA",
            "h1":"DAYTONA",
            "short_description":"Short",
            "long_description_html":"<p>Long</p>",
            "meta_title":"DAYTONA",
            "meta_description":"Meta description",
            "manufacturer_reference_in_specs":"MPN-77",
        }
    return {
        "ready":True,"status":"READY","job_id":20,"item_id":200,
        "identifiers":{
            "channel_reference":ref,
            "channel_reference_role":"PERMANENT_M99_REFERENCE",
            "supplier_reference":supplier,
            "supplier_reference_role":"SUPPLIER_MAPPING_ONLY",
            "manufacturer_reference":"MPN-77",
            "manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY",
        },
        "languages":docs,
        "images":{"count":1,"urls":["https://palltex.bg/i/x.jpg"]},
        "variants":{"groups":1,"rows_count":len(rows),"rows":rows},
    }


def job(status="DRAFT"):
    return SimpleNamespace(id=20,status=status)


def item(url="https://palltex.bg/bg/p/daytona/17374", supplier="042554"):
    return SimpleNamespace(id=200,source_url=url,supplier_reference=supplier)


def test_gate_accepts_valid_palltex_context():
    g=r7k.validate_palltex_controlled_context(job=job(),item=item(),preview=preview(),confirmation=r7k.R7K_CONFIRMATION)
    assert g["canonical_reference"]=="M99-3"
    assert g["supplier_reference"]=="042554"
    assert g["variant_rows"]==2

@pytest.mark.parametrize("bad",["", "PUBLISH", "publish palltex controlled product to m99.eu"])
def test_exact_confirmation_required(bad):
    with pytest.raises(r7k.PalltexControlledPublishError):
        r7k.validate_palltex_controlled_context(job=job(),item=item(),preview=preview(),confirmation=bad)

@pytest.mark.parametrize("url",[
    "http://palltex.bg/bg/p/daytona/17374",
    "https://example.com/bg/p/daytona/17374",
    "https://palltex.bg/category/17374",
    "https://palltex.bg/bg/p/daytona/not-a-number",
])
def test_non_exact_palltex_product_url_blocked(url):
    with pytest.raises(r7k.PalltexControlledPublishError):
        r7k.validate_palltex_controlled_context(job=job(),item=item(url=url),preview=preview(),confirmation=r7k.R7K_CONFIRMATION)

@pytest.mark.parametrize("ref",["M99-1","M99-2"])
def test_protected_historical_identities_blocked(ref):
    with pytest.raises(r7k.PalltexControlledPublishError,match="protected historical identity"):
        r7k.validate_palltex_controlled_context(job=job(),item=item(),preview=preview(ref=ref),confirmation=r7k.R7K_CONFIRMATION)


def test_supplier_reference_mismatch_blocked():
    with pytest.raises(r7k.PalltexControlledPublishError,match="mismatch"):
        r7k.validate_palltex_controlled_context(job=job(),item=item(supplier="DIFF"),preview=preview(),confirmation=r7k.R7K_CONFIRMATION)


def test_variant_quantity_inference_blocked():
    rows=[{"colour":"Антрацит","size":"S","availability":"SUPPLIER_VISIBLE","quantity":30}]
    with pytest.raises(r7k.PalltexControlledPublishError,match="physical stock"):
        r7k.validate_palltex_controlled_context(job=job(),item=item(),preview=preview(rows=rows),confirmation=r7k.R7K_CONFIRMATION)


def test_non_draft_blocked():
    with pytest.raises(r7k.PalltexControlledPublishError,match="DRAFT"):
        r7k.validate_palltex_controlled_context(job=job("READY"),item=item(),preview=preview(),confirmation=r7k.R7K_CONFIRMATION)


def test_publish_delegates_to_proven_canonical_pilot_and_adds_audit(monkeypatch):
    calls={}
    result=CanonicalPilotResult(
        True,"2041","M99-3","0","0","none","26","201","corr","49.90",("en","bg","ru"),api_truth_verified=True,truth_summary="ok"
    )
    def fake_publish(db,**kwargs):
        calls.update(kwargs)
        return result
    monkeypatch.setattr(r7k,"publish_canonical_pilot",fake_publish)
    added=[]
    db=SimpleNamespace(add=lambda x:added.append(x),commit=lambda:None)
    user=SimpleNamespace(id=1,is_superuser=True)
    out=r7k.publish_palltex_controlled(db,user=user,job=job(),item=item(),preview=preview(),category_id=26,price_override="49.90",confirmation=r7k.R7K_CONFIRMATION)
    assert out is result
    assert calls["confirmation"]==r7k.CANONICAL_PILOT_CONFIRMATION
    assert added and added[0].action==r7k.R7K_ACTION


def test_postcondition_rejects_visible_result(monkeypatch):
    bad=CanonicalPilotResult(True,"2041","M99-3","1","0","none","26","201","corr","49.90",("en","bg","ru"),api_truth_verified=True)
    monkeypatch.setattr(r7k,"publish_canonical_pilot",lambda *a,**k:bad)
    db=SimpleNamespace(add=lambda x:None,commit=lambda:None)
    with pytest.raises(r7k.PalltexControlledPublishError,match="postcondition"):
        r7k.publish_palltex_controlled(db,user=SimpleNamespace(id=1,is_superuser=True),job=job(),item=item(),preview=preview(),category_id=26,price_override="49.90",confirmation=r7k.R7K_CONFIRMATION)
