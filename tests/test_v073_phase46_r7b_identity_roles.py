from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_supplier_reconciler import *

def test_supplier_candidate_never_becomes_mpn_implicitly():
    x=manufacturer_identity_gate(supplier_candidate="22160",manufacturer_evidence={"status":"EXACT_CANDIDATE_FOUND","manufacturer_product_code":"22160"})
    assert x["manufacturer_mpn"]==""

def test_equal_text_is_allowed_only_as_separate_verified_roles():
    x=manufacturer_identity_gate(supplier_candidate="22160",manufacturer_evidence={
      "status":"OPERATOR_CONFIRMED_EXACT","manufacturer_product_code_status":"VERIFIED_EXACT_REFERENCE","manufacturer_product_code":"22160"})
    assert x["supplier_reference_candidate"]=="22160"
    assert x["manufacturer_mpn"]=="22160"
    assert x["same_text_allowed_separate_roles"] is True
