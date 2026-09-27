from integrations.bultex99_supplier.models import PublicProduct
from app.services.standard_evidence_policy import StandardApplicability
from app.services.unified_review_evidence import build_unified_review_evidence
def P(std=None):
 return PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764",gross_price_eur=None,availability="OUT_OF_STOCK",standard=std)
def test_uno_supplier_standard_review_ready_but_never_publish_enabled():
 r=build_unified_review_evidence(P("EN ISO:20345:2022+A1:2024"),variant_values=("36","48"),standard_applicability=StandardApplicability.REQUIRED)
 assert r.review_ready and not r.publish_enabled and not r.write_performed
 assert r.standard_provenance=="OBSERVED_SUPPLIER" and r.variants==("36","48")
def test_required_can_fall_back_to_manufacturer():
 r=build_unified_review_evidence(P(),standard_applicability=StandardApplicability.REQUIRED,manufacturer_standard="EN ISO 20345:2022+A1:2024")
 assert r.review_ready and r.standard_provenance=="OBSERVED_MANUFACTURER"
def test_not_applicable_does_not_inherit_old_a6_missing_block():
 r=build_unified_review_evidence(P(),standard_applicability=StandardApplicability.NOT_APPLICABLE)
 assert r.review_ready and "TECHNICAL_STANDARD_MISSING" not in r.blockers
def test_unknown_missing_stays_fail_closed():
 r=build_unified_review_evidence(P(),standard_applicability=StandardApplicability.UNKNOWN)
 assert not r.review_ready and "TECHNICAL_STANDARD_APPLICABILITY_REVIEW" in r.blockers
def test_identity_fusion_still_blocks():
 p=P("EN ISO 20345:2022+A1:2024"); object.__setattr__(p,"supplier_sku","06100764.36")
 assert not build_unified_review_evidence(p,standard_applicability=StandardApplicability.REQUIRED).review_ready
