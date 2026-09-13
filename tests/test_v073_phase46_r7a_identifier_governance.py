from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_evidence_governance import *

def test_blue_is_not_supplier_reference():
    s={"url":"https://calenda.bg/products/31940","supplier_reference":"blue",
       "variants":[{"value":"30White"},{"value":"32 Navy"},{"value":"36 Black"},{"value":"40 Red"}]}
    x=classify_identifier_roles(s)
    assert x["calenda_product_id"]=="31940"
    assert x["supplier_reference"]==""
    assert x["supplier_reference_status"]=="REJECTED_NON_IDENTIFIER_TOKEN"
    assert x["manufacturer_base_mpn"]==""

def test_manufacturer_mpn_requires_exact_confirmed_evidence():
    s={"supplier_reference":"ABC-123"}
    not_exact={"status":"EXACT_CANDIDATE_FOUND","manufacturer_product_code":"65-014-0",
               "manufacturer_product_code_status":"CANDIDATE"}
    assert classify_identifier_roles(s,manufacturer_evidence=not_exact)["manufacturer_base_mpn"]==""
    exact={"status":"OPERATOR_CONFIRMED_EXACT","manufacturer_product_code":"65-014-0",
           "manufacturer_product_code_status":"VERIFIED_EXACT_REFERENCE"}
    x=classify_identifier_roles(s,manufacturer_evidence=exact)
    assert x["supplier_reference"]=="ABC-123"
    assert x["manufacturer_base_mpn"]=="65-014-0"
