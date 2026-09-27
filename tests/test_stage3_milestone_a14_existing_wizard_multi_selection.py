from app.services.product_import_wizard import ImportWizardDraft
from app.services.wizard_multi_selection_bridge import build_existing_wizard_multi_review

def draft(mode,products=(),categories=(),n=None):
 d=ImportWizardDraft();d.selection_mode=mode;d.selected_product_refs=list(products);d.selected_category_refs=list(categories);d.first_n=n;return d

def test_direct_multiple_products_reaches_review():
 r=build_existing_wizard_multi_review(draft("multiple_products",["u1","u2"]),review_one=lambda u:{"product_evidence":{"blockers":[]}})
 assert r["multi_review"].ready_count==2 and r["publish_enabled"] is False

def test_categories_are_not_faked_when_discovery_missing():
 r=build_existing_wizard_multi_review(draft("one_category",categories=["c1"]),review_one=lambda u:{"product_evidence":{"blockers":[]}})
 assert r["selection_blockers"]==("CATEGORY_DISCOVERY_NOT_PROVEN",)

def test_category_discovery_then_per_product_review():
 r=build_existing_wizard_multi_review(draft("multiple_categories",categories=["c1","c2"]),
   discover_category=lambda c:{"c1":["u1","u2"],"c2":["u2","u3"]}[c],
   review_one=lambda u:{"product_evidence":{"blockers":[]}})
 assert r["multi_selection"].product_urls==("u1","u2","u3")
 assert r["multi_review"].ready_count==3

def test_all_site_and_first_n():
 allp=lambda:["u1","u2","u3"]
 a=build_existing_wizard_multi_review(draft("all_products"),discover_all=allp,review_one=lambda u:{"product_evidence":{"blockers":[]}})
 n=build_existing_wizard_multi_review(draft("first_n",n=2),discover_all=allp,review_one=lambda u:{"product_evidence":{"blockers":[]}})
 assert a["multi_review"].ready_count==3 and n["multi_review"].ready_count==2

def test_only_new_requires_filter_and_preserves_scope():
 r=build_existing_wizard_multi_review(draft("only_new_to_m99"),discover_all=lambda:["u1","u2","u3"],
   only_new=lambda xs:["u2"],review_one=lambda u:{"product_evidence":{"blockers":[]}})
 assert r["multi_selection"].product_urls==("u2",)

def test_bad_product_isolated():
 r=build_existing_wizard_multi_review(draft("multiple_products",["ok","bad","ok2"]),
   review_one=lambda u: (_ for _ in ()).throw(RuntimeError()) if u=="bad" else {"product_evidence":{"blockers":[]}})
 assert r["multi_review"].ready_count==2 and r["multi_review"].blocked_count==1
