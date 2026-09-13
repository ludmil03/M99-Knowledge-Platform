import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
import app.services.v073_phase46.content_manufacturer_intelligence as svc

def test_fallback_meta_all_languages_below_hard_threshold():
    profiles=[
        {"name":"ДАМСКА РИЗА TEST","brand":"BRAND","product_type":"shirt","gender":"female","oxford":True,"sizes":["S","M","L"]},
        {"name":"GENERIC PRODUCT","brand":"BRAND","product_type":"product","gender":"unisex","oxford":False,"sizes":[]},
    ]
    for p in profiles:
        for lang in svc.LANGUAGE_REGISTRY:
            short=(svc._localized_title(p,lang)+" "+("S M L" if p.get("sizes") else "")).strip()
            md=svc._fallback_meta_description(p,lang)
            assert md
            assert len(md)<=160
            assert svc._content_similarity(md,short)<0.75

def test_hard_gate_source_contract_still_present():
    s=Path(svc.__file__).read_text(encoding="utf-8")
    assert "if similarity>=0.75:" in s
    assert '"meta_short_distinct_all_languages":True' in s
    assert '"meta_short_threshold":0.75' in s
