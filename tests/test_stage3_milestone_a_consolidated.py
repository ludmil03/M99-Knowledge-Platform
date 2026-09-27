from dataclasses import dataclass
from decimal import Decimal
import pytest
from app.services.stage3_milestone_a_orchestrator import *
from app.services.unified_identity_gate import IdentityDecision,IdentityState
from app.services.content_readiness_gate import LanguageContent

def lang(n="Product"):
    return LanguageContent(n,"short","long technical evidence","meta title","meta description")
def content():
    return {x:lang() for x in ("bg","en","ru","ro")}

@dataclass
class Bultex:
    source_url:str="https://bultex99.example/p/5161"; supplier_product_id:str="5161"
    name:str="Panda UNO LOW"; supplier_sku:str="06100764.36"; brand:str="Panda"
    standard:str="EN ISO 20345:2022+A1:2024"; gross_price_eur:str="58.90"; availability:str="yes"
    legacy_stenso_refs:tuple=()
@dataclass
class Calenda:
    url:str="https://calenda.example/p/a"; source_key:str="CAL-A"; name:str="Calenda Product"
    supplier_reference:str="CA-1";brand:str="Brand";images:tuple=("https://calenda.example/a.webp",)
    price_text:str="100";availability_text:str="yes";currency:str="EUR";calenda_product_id:str="1"
    variants:tuple=();warnings:tuple=()
@dataclass
class Palltex:
    url:str="https://palltex.example/p/a"; source_key:str="PAL-A"; name:str="BWolf Product"
    supplier_reference:str="PA-1";brand:str="BWolf";images:tuple=("https://palltex.example/a.webp",)
    price_text:str="100";availability_text:str="yes";currency:str="EUR";variants:tuple=();warnings:tuple=()

@pytest.mark.parametrize("supplier,obj,ref",[
 ("BULTEX99",Bultex(),"06100764.36"),
 ("CALENDA",Calenda(),"CAL-A"),
 ("PALLTEX",Palltex(),"PAL-A")])
def test_three_proven_supplier_golden_paths(supplier,obj,ref):
    # source_ref may prefer supplier SKU for Bultex and source key for others.
    probe=build_unified_intake_plan(supplier_key=supplier,hydrated_products=[obj],requested_targets=["m99.eu"])
    actual=probe.items[0].source_ref
    decision={actual:IdentityDecision(actual,IdentityState.NEW)}
    q={actual:ProductQualityInput(actual,content(),Decimal("100"),Decimal("1.31"),Decimal("20"),True)}
    plan=build_milestone_a_plan(supplier_key=supplier,hydrated_products=[obj],requested_targets=["m99.eu"],
        identity_decisions=decision,quality_inputs=q)
    assert plan.ready_for_operator_review is True
    assert plan.publish_enabled is False and plan.write_performed is False
    assert plan.ready_targets==("m99.eu",)

def test_uno_low_price_golden():
    obj=Bultex()
    probe=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[obj],requested_targets=["m99.eu"])
    ref=probe.items[0].source_ref
    q={ref:ProductQualityInput(ref,content(),Decimal("58.90"),Decimal("1.31"),Decimal("20"),True)}
    p=build_milestone_a_plan(supplier_key="BULTEX99",hydrated_products=[obj],requested_targets=["m99.eu"],
      identity_decisions={ref:IdentityDecision(ref,IdentityState.NEW)},quality_inputs=q)
    assert p.products[0].price_vat.target_gross==Decimal("58.13")

def test_ambiguous_identity_fails_closed():
    obj=Palltex(); probe=build_unified_intake_plan(supplier_key="PALLTEX",hydrated_products=[obj],requested_targets=["m99.eu"])
    ref=probe.items[0].source_ref
    p=build_milestone_a_plan(supplier_key="PALLTEX",hydrated_products=[obj],requested_targets=["m99.eu"],
      identity_decisions={ref:IdentityDecision(ref,IdentityState.AMBIGUOUS)},quality_inputs={})
    assert not p.ready_for_operator_review and not p.publish_enabled

def test_unproven_target_does_not_become_ready():
    obj=Calenda(); probe=build_unified_intake_plan(supplier_key="CALENDA",hydrated_products=[obj],requested_targets=["alviro.ro"])
    ref=probe.items[0].source_ref
    p=build_milestone_a_plan(supplier_key="CALENDA",hydrated_products=[obj],requested_targets=["alviro.ro"],
      identity_decisions={ref:IdentityDecision(ref,IdentityState.NEW)},quality_inputs={})
    assert not p.ready_for_operator_review and "alviro.ro" in p.blocked_targets

def test_missing_quality_fails_closed():
    obj=Bultex(); probe=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[obj],requested_targets=["m99.eu"])
    ref=probe.items[0].source_ref
    p=build_milestone_a_plan(supplier_key="BULTEX99",hydrated_products=[obj],requested_targets=["m99.eu"],
      identity_decisions={ref:IdentityDecision(ref,IdentityState.NEW)},quality_inputs={})
    assert "QUALITY_INPUT_MISSING:"+ref in p.blockers
    assert not p.ready_for_operator_review

def test_unknown_supplier_fails_closed():
    with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
        build_milestone_a_plan(supplier_key="FEYA",hydrated_products=[Palltex()],requested_targets=["m99.eu"],
          identity_decisions={},quality_inputs={})
