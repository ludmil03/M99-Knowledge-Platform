from pathlib import Path
from types import SimpleNamespace
import importlib
from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT=Path(__file__).resolve().parents[1]
ADMIN=ROOT/"admin-platform"

def test_all_add_products_templates_compile():
    env=Environment(loader=FileSystemLoader(str(ADMIN/"app"/"templates")))
    for name in ("add_products/workspace.html","add_products/r37_prepare.html","add_products/r37_canonical_preview.html"):
        env.get_template(name)

def test_frozen_r37_contracts_preserved():
    router=(ADMIN/"app/routers/r37_add_products_flow.py").read_text(encoding="utf-8").lower()
    assert "publish" not in router
    prep=(ADMIN/"app/templates/add_products/r37_prepare.html").read_text(encoding="utf-8")
    assert "{% if bridge.bridge_ready %}" in prep
    assert "Потвърди Identity и създай DRAFT" in prep

def test_supplier_availability_ownership_boundary_matches_legacy_contract():
    bridge=(ADMIN/"app/services/v073_phase45/r37_import_bridge.py").read_text(encoding="utf-8").lower()
    assert "inventory" not in bridge
    assert "stock" not in bridge

def _river_fixture():
    variants=[]
    for vi,code in enumerate(("26","42","44","46")):
        sizes=[]
        for si,size in enumerate(("S","M","L","XL","XXL","XXXL")):
            status="OUT_OF_STOCK" if si==5 else "IN_STOCK"
            total=0 if status=="OUT_OF_STOCK" else 3
            sizes.append({"size":size,"price_eur":"20.40" if size!="XXXL" else "21.47","supplier_availability":{"varna_qty":total,"delivery_1_2_days_qty":0,"delivery_7_10_days_qty":0,"total_observed_qty":total,"status":status,"evidence_scope":"SUPPLIER","counts_as_m99_owned_stock":False}})
        variants.append({"type":"COLOR","value":f"Color {code}","code":code,"image_url":f"https://calenda.bg/storage/products/93100_{code}.jpg","sizes":sizes})
    # Historical accepted evidence is 20 available / 4 OOS: one OOS per color.
    return SimpleNamespace(url="https://calenda.bg/products/31809",name="МЪЖКА РИЗА RIVER",supplier_reference="93100",source_key="31809",calenda_product_id="31809",brand="PROMO STARS",price_text="FROM 20.40",currency="EUR",availability_text="AVAILABLE BY VARIANT",description="x",specifications=(),images=("https://calenda.bg/storage/products/93100_26.jpg",),variants=tuple(variants),warnings=())

def test_river_snapshot_contract():
    from app.services.v073_phase45.r37_import_bridge import supplier_evidence_snapshot
    snap=supplier_evidence_snapshot(_river_fixture())
    s=snap["evidence_summary"]
    assert s["variant_count"]==4
    assert s["color_size_rows"]==24
    assert s["available_rows"]==20
    assert s["unavailable_rows"]==4
    assert s["unique_images"]==4
    assert s["supplier_availability_not_owned"] is True

def test_draft_snapshot_is_previewable_without_live_refetch():
    from app.services.v073_phase45.r37_import_bridge import supplier_evidence_snapshot
    snap=supplier_evidence_snapshot(_river_fixture())
    assert snap["snapshot_source"]=="DRAFT"
    assert len(snap["images"])==4
    assert sum(len(v.get("sizes") or []) for v in snap["variants"])==24

def test_workspace_has_evidence_projection():
    text=(ADMIN/"app/templates/add_products/workspace.html").read_text(encoding="utf-8")
    assert "M99_PHASE46_R2_EVIDENCE_MATRIX" in text
    assert "Цветови изображения" in text
    assert "Color × Size evidence" in text
    assert "M99 physical stock" in text

def test_canonical_preview_uses_draft_snapshot_path():
    router=(ADMIN/"app/routers/r37_add_products_flow.py").read_text(encoding="utf-8")
    assert "product_for_canonical_preview_from_draft" in router
    bridge=(ADMIN/"app/services/v073_phase45/r37_import_bridge.py").read_text(encoding="utf-8")
    assert '"supplier_evidence": evidence' in bridge
    assert '"identity": _json_safe(identity)' in bridge
    assert "LIVE_FALLBACK_PRE_R2_DRAFT" in bridge
