from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
for p in (ROOT,ADMIN):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
from app.services.bultex99_wizard_bridge import is_bultex_source,build_bultex_dry_run,identity_summary
from integrations.bultex99_supplier.models import PublicProduct,IdentityPreview

REG={"mela99.com":(True,True),"m99.eu":(True,True),"alviro.ro":(True,False),"toplinka.com":(False,False)}
P=[PublicProduct("101","https://bultex99.com/products/101-a","A",category_refs=("cat-a",)),
   PublicProduct("102","https://bultex99.com/products/102-b","B",category_refs=("cat-b",)),
   PublicProduct("103","https://bultex99.com/products/103-c","C",category_refs=("cat-a",))]
IDS={"101":IdentityPreview("101","NEW"),"102":IdentityPreview("102","EXISTING"),
     "103":IdentityPreview("103","AMBIGUOUS")}

def report(mode,products=(),cats=(),n=None,targets=("mela99.com",)):
 return build_bultex_dry_run(selection_mode=mode,product_refs=list(products),category_refs=list(cats),first_n=n,
 products=P,identities=IDS,requested_targets=list(targets),target_registry=REG)

def test_source_is_exact(): assert is_bultex_source("org-bultex") and not is_bultex_source("org-palltex")
def test_one_product(): assert report("one_product",("101",))["selected_count"]==1
def test_multiple_products(): assert report("multiple_products",("101","102"))["selected_count"]==2
def test_one_category(): assert report("one_category",cats=("cat-a",))["selected_count"]==2
def test_multiple_categories(): assert report("multiple_categories",cats=("cat-a","cat-b"))["selected_count"]==3
def test_all_products(): assert report("all_products")["selected_count"]==3
def test_first_n(): assert report("first_n",n=2)["selected_count"]==2
def test_only_new(): assert [x["supplier_product_id"] for x in report("only_new_to_m99")["items"]]==["101"]
def test_manual(): assert report("manual_selection",("102","103"))["selected_count"]==2
def test_ambiguous_blocks_item():
 x=report("one_product",("103",))["items"][0];assert x["qa_status"]=="BLOCKED" and "IDENTITY_AMBIGUOUS" in x["qa_errors"]
def test_target_intersection():
 x=report("one_product",("101",),targets=("m99.eu","alviro.ro","toplinka.com"))
 assert x["ready_targets"]==["m99.eu"] and x["blocked_targets"]==["alviro.ro","toplinka.com"]
def test_no_write(): assert report("all_products")["write_performed"] is False
def test_summary(): assert identity_summary(report("all_products"))=="NEW: 1 / EXISTING: 1 / AMBIGUOUS: 1"
def test_router_contract_no_write_tokens():
 s=(ADMIN/"app/routers/bultex99_import_preview.py").read_text()
 for t in ("requests.post(","create_product(","/api/products","DELETE ","process.kill"): assert t not in s
def test_palltex_not_modified_by_payload():
 assert not any("palltex" in str(p).lower() for p in (ROOT/"admin-platform").glob("**/*") if "bultex99" in p.name.lower())
