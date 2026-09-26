from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from integrations.bultex99_supplier.public_parser import *
from integrations.bultex99_supplier.pipeline import *
from integrations.bultex99_supplier.models import *
from integrations.bultex99_supplier.legacy_stenso import *
from tests.fixtures_bultex99_v1 import PRODUCT_HTML,COLLECTION_HTML

def products():
 return [
  PublicProduct("1","https://bultex99.com/products/1-a","A",category_refs=("c1",)),
  PublicProduct("2","https://bultex99.com/products/2-b","B",category_refs=("c1","c2")),
  PublicProduct("3","https://bultex99.com/products/3-c","C",category_refs=("c2",)),
 ]
def test_real_shape_parser():
 p=parse_public_product(PRODUCT_HTML,"https://bultex99.com/products/2033-kanton")
 assert (p.supplier_product_id,p.supplier_sku,str(p.gross_price_eur),p.availability)==("2033","50319004","6.20","IN_STOCK")
 assert p.standard=="EN 397:2012+A1:2012"
def test_collection_dedup(): assert len(extract_collection_product_urls(COLLECTION_HTML))==2
def test_reject_foreign_product_url():
 import pytest
 with pytest.raises(Bultex99PublicParseError): product_id_from_url("https://example.com/x")
def test_one(): assert [x.supplier_product_id for x in select_products(SelectionRequest("one_product",("1",)),products())]==["1"]
def test_multiple(): assert len(select_products(SelectionRequest("multiple_products",("1","3")),products()))==2
def test_one_category(): assert len(select_products(SelectionRequest("one_category",category_refs=("c1",)),products()))==2
def test_multiple_categories(): assert len(select_products(SelectionRequest("multiple_categories",category_refs=("c1","c2")),products()))==3
def test_all(): assert len(select_products(SelectionRequest("all_products"),products()))==3
def test_first_n(): assert len(select_products(SelectionRequest("first_n",first_n=2),products()))==2
def test_only_new():
 ids={"1":IdentityPreview("1","EXISTING"),"2":IdentityPreview("2","NEW")}
 assert [x.supplier_product_id for x in select_products(SelectionRequest("only_new_to_m99"),products(),ids)]==["2","3"]
def test_manual(): assert [x.supplier_product_id for x in select_products(SelectionRequest("manual_selection",("2",)),products())]==["2"]
def test_bad_selection_fail_closed():
 import pytest
 with pytest.raises(ValueError): select_products(SelectionRequest("first_n",first_n=0),products())
def test_target_intersection():
 r=resolve_targets(["mela99.com","alviro.ro","toplinka.com","unknown"],{"mela99.com":(True,True),"alviro.ro":(True,False),"toplinka.com":(False,False)})
 assert r[2]==["mela99.com"] and set(r[3])=={"alviro.ro","toplinka.com","unknown"}
def test_ambiguous_identity_blocked():
 p=products()[0]; s,e=qa(p,IdentityPreview("1","AMBIGUOUS")); assert s=="BLOCKED" and e
def test_unresolved_identity_blocked():
 p=products()[0]; s,e=qa(p,IdentityPreview("1","UNRESOLVED")); assert s=="BLOCKED"
def test_dry_run_never_writes():
 rep=build_dry_run(SelectionRequest("all_products"),products(),{},["mela99.com"],{"mela99.com":(True,True)})
 assert rep.write_performed is False and rep.ready_targets==["mela99.com"]
def test_legacy_stenso_evidence_only():
 u="https://stenso.net/produkt/medicinski-pantaloni/4594-foo"
 assert legacy_stenso_product_id(u)=="4594"
 assert migration_evidence("4594",[u])==[u]
def test_legacy_is_evidence_only():
 u="https://stenso.net/produkt/x/4594-foo"
 evidence=migration_evidence("4594",[u])
 assert evidence==[u]
 assert all(not x.startswith("M99 ") for x in evidence)
def test_no_network_import_in_pipeline():
 import inspect
 s=inspect.getsource(sys.modules["integrations.bultex99_supplier.pipeline"])
 assert "requests" not in s and "httpx" not in s
def test_no_write_api_in_package():
 text="\n".join(p.read_text(encoding="utf-8") for p in (ROOT/"integrations/bultex99_supplier").glob("*.py"))
 for token in ["requests.post(","create_product(","delete_product(","/api/products"]:
  assert token not in text
