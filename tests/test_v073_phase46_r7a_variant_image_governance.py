from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_evidence_governance import *

def test_same_image_across_four_colors_is_generic_shared():
    s={"variants":[
      {"value":"30 White","image_url":"https://x/a.jpg"},
      {"value":"32 Navy","image_url":"https://x/a.jpg"},
      {"value":"36 Black","image_url":"https://x/a.jpg"},
      {"value":"40 Red","image_url":"https://x/a.jpg"},
    ]}
    rows=classify_variant_images(s)
    assert {x["image_provenance"] for x in rows}=={"SUPPLIER_GENERIC_SHARED"}
    assert not any(x["safe_as_exact_variant_image"] for x in rows)

def test_explicit_unique_variant_images_can_be_exact():
    s={"variants":[
      {"value":"White","image_url":"https://x/w.jpg","image_association_exact":True},
      {"value":"Black","image_url":"https://x/b.jpg","image_association_exact":True},
    ]}
    rows=classify_variant_images(s)
    assert all(x["image_provenance"]=="SUPPLIER_VARIANT_EXACT" for x in rows)
