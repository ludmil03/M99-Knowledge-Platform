from pathlib import Path
import sys,itertools
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_evidence_governance import *

def test_large_product_agnostic_matrix():
    brands=["BRAND_A","BRAND_B","BRAND_C","BRAND_D","BRAND_E","BRAND_F","BRAND_G","BRAND_H"]
    refs=["ABC-123","65-014-0","K1234","93100","ID35","blue","Navy","XL"]
    colors=["White","Navy","Black","Red","Green","Yellow"]
    checked=0
    for brand,ref,n in itertools.product(brands,refs,range(1,7)):
        variants=[]
        shared="https://example.test/shared.jpg"
        for i,c in enumerate(colors[:n]):
            variants.append({"value":c,"code":f"C{i}","image_url":shared if n>1 else f"https://example.test/{i}.jpg"})
        s={"url":f"https://calenda.bg/products/{30000+checked}","brand":brand,"supplier_reference":ref,"variants":variants}
        snap=build_calenda_evidence_snapshot(s)
        validate_snapshot(snap)
        if ref.casefold() in {"blue","navy","xl"}:
            assert snap["identifiers"]["supplier_reference"]==""
        else:
            assert snap["identifiers"]["supplier_reference"]==ref
        if n>1:
            assert all(v["image_provenance"]=="SUPPLIER_GENERIC_SHARED" for v in snap["variant_images"])
        checked+=1
    assert checked==384
