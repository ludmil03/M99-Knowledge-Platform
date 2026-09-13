from pathlib import Path
import sys,json
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_supplier_reconciler import *
DATA=json.loads((ROOT/"tests/fixtures/calenda_r7a_observed_matrix_20260910.json").read_text(encoding="utf-8"))

def test_all_observed_rows_reconcile_without_manufacturer_invention():
    assert len(DATA["products"])==13
    for row in DATA["products"]:
        x=reconcile_observed_product(row)
        assert x["calenda_product_id"]==row["product_id"]
        assert x["manufacturer_mpn"]==""

def test_calenda_id_codes_are_not_supplier_or_manufacturer_codes():
    rows=[x for x in DATA["products"] if str(x["page_code_candidate"]).upper().startswith("ID")]
    assert len(rows)>=6
    for row in rows:
        x=reconcile_observed_product(row)
        assert x["page_code_role"]=="CALENDA_CATALOG_CODE"
        assert x["supplier_reference_candidate"]==""
        assert x["manufacturer_mpn"]==""

def test_punt_and_numeric_codes_remain_supplier_candidates_only():
    for row in DATA["products"]:
        code=str(row["page_code_candidate"])
        if code.startswith("PUNT-") or code.isdigit():
            x=reconcile_observed_product(row)
            assert x["supplier_reference_candidate"]==code
            assert x["manufacturer_mpn"]==""

def test_brand_boundary_cleanup_is_generic():
    assert clean_supplier_brand("BRAND X Допълнителна информация")=="BRAND X"
    assert clean_supplier_brand("BRAND Y Подобни продукти ID123 OTHER")=="BRAND Y"
