from app.services.product_import_wizard import ImportWizardDraft
from app.services.stage3_final_unified_intake import build_stage3_final_review

def d(mode,p=(),c=(),n=None):
 x=ImportWizardDraft();x.selection_mode=mode;x.selected_product_refs=list(p);x.selected_category_refs=list(c);x.first_n=n
 x.requested_targets=["m99.eu","alviro.ro"];x.ready_targets=["m99.eu"];x.blocked_targets=["alviro.ro"];return x
def good(u):return {"product_evidence":{"blockers":[]}}
def test_eight_modes():
 cases=[
 (d("one_product",["u1"]),{},1),(d("multiple_products",["u1","u2"]),{},2),
 (d("one_category",c=["c"]),{"discover_category":lambda c:["u1","u2"]},2),
 (d("multiple_categories",c=["a","b"]),{"discover_category":lambda c:{"a":["u1"],"b":["u2","u3"]}[c]},3),
 (d("all_products"),{"discover_all":lambda:["u1","u2","u3"]},3),
 (d("first_n",n=2),{"discover_all":lambda:["u1","u2","u3"]},2),
 (d("only_new_to_m99"),{"discover_all":lambda:["u1","u2"],"only_new":lambda xs:["u2"]},1),
 (d("manual_selection",["u3","u1"]),{},2)]
 for draft,kw,count in cases:
  r,_=build_stage3_final_review(draft,review_one=good,**kw)
  assert r.resolved_count==count and r.ready_count==count and not r.selection_blockers
  assert r.publish_enabled is False and r.write_performed is False
def test_partial_failure_isolation():
 def one(u):return {"product_evidence":{"blockers":["IDENTITY_AMBIGUOUS"] if u=="bad" else []}}
 r,_=build_stage3_final_review(d("multiple_products",["ok","bad","ok2"]),review_one=one,max_products_per_batch=2)
 assert (r.ready_count,r.blocked_count)==(2,1)
def test_1000_products_batch_invariance():
 urls=[f"u{i}" for i in range(1000)]
 r,_=build_stage3_final_review(d("all_products"),discover_all=lambda:urls,review_one=good,max_products_per_batch=37)
 assert (r.resolved_count,r.ready_count)==(1000,1000)
def test_missing_discovery_fails_closed():
 for x in (d("one_category",c=["c"]),d("all_products")):
  r,_=build_stage3_final_review(x,review_one=good)
  assert r.selection_blockers and r.resolved_count==0
def test_missing_review_adapter_fails_closed():
 r,_=build_stage3_final_review(d("multiple_products",["u1","u2"]))
 assert r.selection_blockers==("REVIEW_ADAPTER_NOT_PROVEN",)
