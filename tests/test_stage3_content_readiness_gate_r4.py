from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.unified_product_intake import build_unified_intake_plan
from app.services.unified_identity_gate import *
from app.services.canonical_draft_gate import build_canonical_drafts
from app.services.content_readiness_gate import *
def draft():
 p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
 x=build_unified_intake_plan(supplier_key="BULTEX99",hydrated_products=[p],requested_targets=["m99.eu"])
 x=apply_identity_decisions(x,{"06100764.36":IdentityDecision("06100764.36",IdentityState.NEW)})
 return build_canonical_drafts(x)[0]
def c(n="UNO LOW"):return LanguageContent(n,"short","long technical evidence","meta title","meta description")
def test_all_four_canonical_languages_ready():
 x=evaluate_content_readiness(draft(),{k:c() for k in CANONICAL_LANGUAGES})
 assert x.ready and not x.blockers and not x.write_performed
def test_missing_language_blocks():
 x=evaluate_content_readiness(draft(),{"bg":c(),"en":c(),"ru":c()})
 assert not x.ready and "MISSING_LANGUAGE:ro" in x.blockers
def test_missing_mandatory_field_blocks():
 x=evaluate_content_readiness(draft(),{k:c() for k in CANONICAL_LANGUAGES}|{"bg":LanguageContent("UNO LOW","","long","meta","desc")})
 assert "MISSING_CONTENT:bg:short" in x.blockers
def test_channel_subset_can_be_checked_without_erasing_canonical_policy():
 x=evaluate_content_readiness(draft(),{"en":c(),"bg":c(),"ru":c()},("en","bg","ru"))
 assert x.ready
