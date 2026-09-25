from decimal import Decimal
from app.services.v073_phase46.product_import_mvp import *

def product(existing=None, price="100"):
    return ProductCandidate(
      "M99 100018", SupplierCommercial("palltex","042502",True,Decimal(price),"BGN","rev-1","IN_STOCK"),
      "042502", {"EN":{"name":"x"},"BG":{"name":"x"},"RU":{"name":"x"}},
      (Variant("42","42",True),Variant("43","43",False)),
      (ImageEvidence("https://supplier/item.webp","SUPPLIER",True,True,"abc"),),
      existing or {}
    )
def cfg(**kw):
    d=dict(channel_id="m99eu",market="BG",currency="EUR",requested=True,authorized=True,ready=True,
           category_id=26,tax_rules_group_id=5,vat_rate=Decimal("0.20"),languages=("EN","BG","RU"),platform="prestashop9")
    d.update(kw); return ChannelConfig(**d)

def test_price_policy_range_and_stability():
    p=product(); a=pricing_decision(p); b=pricing_decision(p,a)
    assert Gate.AUTO_READY==a.gate and Decimal("0.0100")<=a.discount_rate<=Decimal("0.0170")
    assert a.discount_rate==b.discount_rate and a.target_gross<Decimal("100")
def test_existing_2041_is_update_never_create():
    p=product({"m99eu":"2041"}); x=plan_channel(p,cfg())
    assert x.operation=="UPDATE" and x.gate==Gate.AUTO_READY
def test_missing_channel_mapping_is_create():
    assert plan_channel(product(),cfg()).operation=="CREATE"
def test_multichannel_only_requested():
    cs=(cfg(),cfg(channel_id="mela99",requested=False,platform="thirtybees"),cfg(channel_id="laviro",requested=True,platform="prestashop16"))
    assert [x.channel_id for x in plan_selected_channels(product(),cs)]==["m99eu","laviro"]
def test_vat_ambiguity_blocks():
    assert plan_channel(product(),cfg(tax_rules_group_id=None)).gate==Gate.BLOCKED
def test_default_variant_required():
    p=product(); p=ProductCandidate(p.m99_id,p.supplier,p.manufacturer_mpn,p.localized_content,(Variant("42","42"),),p.images,p.existing_channel_ids)
    assert plan_channel(p,cfg()).gate==Gate.BLOCKED
def test_image_required():
    p=product(); p=ProductCandidate(p.m99_id,p.supplier,p.manufacturer_mpn,p.localized_content,p.variants,(),p.existing_channel_ids)
    assert plan_channel(p,cfg()).gate==Gate.BLOCKED
def test_quality_readback():
    pl=plan_channel(product({"m99eu":"2041"}),cfg())
    actual={"reference":"M99 100018","active":"0","available_for_order":"0","visibility":"none","category_id":26,
            "gross_price":pl.target_gross,"tax_rules_group_id":5,"image_count":1,"combination_count":2,"default_combination_count":1}
    assert quality_readback(pl,actual,expected_reference="M99 100018",expected_images=1,expected_combinations=2)[0]==Gate.AUTO_READY
def test_api_success_business_failure_is_blocked():
    pl=plan_channel(product({"m99eu":"2041"}),cfg())
    actual={"reference":"M99 100018","active":"0","available_for_order":"0","visibility":"none","category_id":26,
            "gross_price":"0.00","tax_rules_group_id":5,"image_count":1,"combination_count":2,"default_combination_count":1}
    assert quality_readback(pl,actual,expected_reference="M99 100018",expected_images=1,expected_combinations=2)[0]==Gate.BLOCKED
