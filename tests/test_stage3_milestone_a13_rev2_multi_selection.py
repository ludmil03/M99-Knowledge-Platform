from app.services.multi_selection_orchestration import *
def test_all_modes_are_preserved():
 assert set(SUPPORTED_SELECTION_MODES)=={"one_product","multiple_products","one_category","multiple_categories","all_products","first_n","only_new_to_m99","manual_selection"}
def test_one_and_multiple_products():
 assert resolve_selection("one_product",product_refs=["u1"]).product_urls==("u1",)
 assert resolve_selection("multiple_products",product_refs=["u1","u2"]).product_urls==("u1","u2")
def test_one_and_multiple_categories_discover_products():
 m={"c1":["u1","u2"],"c2":["u2","u3"]}
 assert resolve_selection("one_category",category_refs=["c1"],discover_category=lambda c:m[c]).product_urls==("u1","u2")
 r=resolve_selection("multiple_categories",category_refs=["c1","c2"],discover_category=lambda c:m[c])
 assert r.product_urls==("u1","u2","u3") and r.discovery_pages==2
def test_all_site_first_n_only_new_manual():
 allp=lambda:["u1","u2","u3","u4"]
 assert resolve_selection("all_products",discover_all=allp).product_urls==("u1","u2","u3","u4")
 assert resolve_selection("first_n",discover_all=allp,first_n=2).product_urls==("u1","u2")
 assert resolve_selection("only_new_to_m99",discover_all=allp,only_new=lambda xs:[x for x in xs if x in ("u2","u4")]).product_urls==("u2","u4")
 assert resolve_selection("manual_selection",product_refs=["u4","u1"]).product_urls==("u4","u1")
def test_batch_safety_does_not_change_business_selection():
 s=resolve_selection("all_products",discover_all=lambda:[f"u{i}" for i in range(123)])
 seen=[]
 r=build_multi_selection_review(s,review_one=lambda u:(seen.append(u) or {"product_evidence":{"blockers":[]}}),max_products_per_batch=17)
 assert len(seen)==123 and r.ready_count==123 and r.blocked_count==0 and r.publish_enabled is False
def test_one_bad_product_does_not_poison_ready_products():
 s=resolve_selection("multiple_products",product_refs=["good1","bad","good2"])
 def one(u):
  if u=="bad": raise RuntimeError("supplier parse")
  return {"product_evidence":{"blockers":[]}}
 r=build_multi_selection_review(s,review_one=one,max_products_per_batch=2)
 assert [x.status for x in r.items]==["READY","BLOCKED","READY"]
 assert r.ready_count==2 and r.blocked_count==1
def test_missing_discovery_fails_closed_without_fabrication():
 assert resolve_selection("one_category",category_refs=["c"]).blockers==("CATEGORY_DISCOVERY_NOT_PROVEN",)
 assert resolve_selection("all_products").blockers==("SITE_DISCOVERY_NOT_PROVEN",)
