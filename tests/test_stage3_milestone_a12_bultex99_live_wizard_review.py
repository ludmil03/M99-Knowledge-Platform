import pytest
from app.services.bultex99_readonly_hydration import BultexHydrationError
from app.services.standard_evidence_policy import StandardApplicability
from app.services.bultex99_live_wizard_review import build_bultex99_live_wizard_review
URL="https://bultex99.com/products/5161-rabotni-obuvki-uno-low-s3s-fo-lg-sr-esd"
HTML="<html><h1>Работни обувки UNO LOW S3S FO LG SR ESD</h1><div>Арт. № 06100764</div><div>58.90 €</div><div>EN ISO:20345:2022+A1:2024</div></html>"
def test_exact_a3_tuple_contract_one_get_review_only():
 calls=[]
 def get(u):
  calls.append(u); return (200,URL,HTML)
 r=build_bultex99_live_wizard_review(URL,get=get,variant_values=tuple(str(x) for x in range(36,49)),standard_applicability=StandardApplicability.REQUIRED)
 assert len(calls)==1 and r.get_count==1 and not r.write_performed
 e=r.context["product_evidence"]
 assert e["supplier_product_id"]=="5161" and e["supplier_product_sku"]=="06100764"
 assert len(e["variants"])==13 and e["standard_provenance"]=="OBSERVED_SUPPLIER"
 assert r.context["publish_enabled"] is False and r.context["write_performed"] is False
def test_wrong_host_exact_a3_exception_and_zero_get():
 calls=[]
 with pytest.raises(BultexHydrationError,match="BULTEX_URL_NOT_ALLOWED"):
  build_bultex99_live_wizard_review("https://example.com/products/5161-x",get=lambda u:calls.append(u))
 assert calls==[]
def test_regression_rejects_old_simplenamespace_style_contract():
 class R: status_code=200; url=URL; text=HTML
 with pytest.raises(TypeError,match="BULTEX_GET_CONTRACT"):
  build_bultex99_live_wizard_review(URL,get=lambda u:R())
def test_cross_host_redirect_still_fails_closed():
 with pytest.raises(BultexHydrationError):
  build_bultex99_live_wizard_review(URL,get=lambda u:(200,"https://example.com/products/5161-x",HTML))
