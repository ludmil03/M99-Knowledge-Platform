import importlib
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN = REPO_ROOT / "admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

LANGS=("BG","EN","RU","RO","GR")

def _profile():
    return {
        "brand":"PROMO STARS","model":"RIVER","reference":"93100","oxford":True,
        "composition":"70% cotton / 30% polyester","weight_gsm":130,
        "classic_cut":True,"chest_pocket":True,"stiff_collar":True,
        "oeko_tex":True,"sizes":["S","M","L","XL","XXL","XXXL"],
        "colors":["white","black","navy","sky blue"],"images":[],"official_tables":[],
    }

def test_meta_and_short_are_materially_different_for_all_registered_languages():
    svc=importlib.import_module("app.services.v073_phase46.content_manufacturer_intelligence")
    docs={lang:svc._doc(_profile(),lang) for lang in LANGS}
    scores=svc._validate_meta_short_distinctness(docs)
    assert set(scores)==set(LANGS)
    for lang in LANGS:
        d=docs[lang]
        assert d["meta_description"] != d["short_description"]
        assert svc._normalized_content_text(d["meta_description"]) != svc._normalized_content_text(d["short_description"])
        assert d["quality_metrics"]["meta_short_similarity"] < 0.75
        assert scores[lang] < 0.75

def test_m99eu_bundle_en_bg_ru_cannot_pass_with_duplicate_meta_short():
    svc=importlib.import_module("app.services.v073_phase46.content_manufacturer_intelligence")
    bundle=svc.build_content_bundle(
        supplier_evidence={"name":"МЪЖКА РИЗА RIVER","supplier_reference":"93100","brand_evidence":"PROMO STARS"},
        manufacturer_evidence={"status":"OPERATOR_CONFIRMED_EXACT","manufacturer_product_code":"93100","text_excerpt":"Oxford 70% cotton 30% polyester 130 g/m² OEKO-TEX classic cut chest pocket","images":[],"tables":[]},
        target_code="m99eu",
    )
    assert bundle["schema"]=="m99.phase46.r3.content_bundle.v3"
    assert bundle["identifier_governance"]["supplier_reference_role"]=="SUPPLIER_MAPPING_ONLY"
    assert bundle["identifier_governance"]["manufacturer_reference_role"]=="VERIFIED_MANUFACTURER_MPN_ONLY"
    assert bundle["identifier_governance"]["channel_reference_role"]=="PERMANENT_M99_REFERENCE"
    assert set(bundle["documents"])=={"EN","BG","RU"}
    assert bundle["quality"]["meta_short_distinct_all_languages"] is True
    assert bundle["quality"]["meta_short_threshold"]==0.75
    assert all(v<0.75 for v in bundle["quality"]["meta_short_similarity_scores"].values())

def test_exact_duplicate_is_release_blocking():
    svc=importlib.import_module("app.services.v073_phase46.content_manufacturer_intelligence")
    try:
        svc._validate_meta_short_distinctness({"EN":{"meta_description":"same text","short_description":"same text"}})
    except ValueError as exc:
        assert "EN:exact" in str(exc)
    else:
        raise AssertionError("Exact duplicate was not rejected")
