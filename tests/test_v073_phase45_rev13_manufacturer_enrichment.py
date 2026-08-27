from pathlib import Path
import importlib.util

ROOT=Path(__file__).resolve().parents[1]
SERVICE=ROOT/"admin-platform/app/services/manufacturer_enrichment.py"
SUPPLIER=ROOT/"admin-platform/app/services/supplier_browser.py"
TEMPLATE=ROOT/"admin-platform/app/templates/supplier_browser/index.html"
REVIEW=ROOT/"admin-platform/app/templates/supplier_browser/manufacturer_review.html"
ROUTER=ROOT/"admin-platform/app/routers/supplier_browser.py"

def load(path, name):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

PANDA_HTML="""
<html><head><title>MARINE - PANDA SAFETY</title></head><body>
<h2>MARINE</h2>
<h2>Code</h2><div>98090 O2 FO SR</div>
<h2>EN ISO</h2><div>20347:2022 +A1:2024</div>
<h2>Category of Protection</h2><div>O2</div>
<h2>Slip Resistance</h2><div>SR</div>
<h2>Size Range</h2><div>35-50</div>
<h2>Weight</h2><div>640gr</div>
<a href="/tds/marine.pdf">Technical Data Sheet (TDS)</a>
<div>UPPER - Expand Tab for Further Details</div>
<div>Natural leather with exceptional water-repellent properties and outstanding tensile strength.</div>
<img src="/images/marine.jpg" alt="MARINE">
</body></html>
"""

def test_panda_official_product_parser_contract():
    m=load(SERVICE,"manufacturer_enrichment")
    p=m.parse_panda_safety("https://pandasafety.com/product/marine/",PANDA_HTML,200)
    assert p["model"]=="MARINE"
    assert p["manufacturer_code"]=="98090 O2 FO SR"
    assert "20347:2022" in p["en_iso"]
    assert p["protection_class"]=="O2"
    assert p["slip_resistance"]=="SR"
    assert p["size_range"]=="35-50"
    assert p["weight"]=="640gr"
    assert p["tds_url"].endswith("/tds/marine.pdf")
    assert p["images"]

def test_identity_keeps_supplier_and_manufacturer_codes_separate():
    m=load(SERVICE,"manufacturer_enrichment2")
    supplier={"title":"Обувки PANDA MARINE O2 FO SRC","supplier_reference":"06200280"}
    manufacturer={"model":"MARINE","manufacturer_code":"98090 O2 FO SR"}
    x=m.compare_identity(supplier,manufacturer)
    assert x["model_match"] is True
    assert x["supplier_reference"]=="06200280"
    assert x["manufacturer_code"]=="98090 O2 FO SR"
    assert x["requires_operator_confirmation"] is True

def test_merged_evidence_source_authority():
    m=load(SERVICE,"manufacturer_enrichment3")
    supplier={"title":"MARINE","supplier_reference":"S1","price_text":"120 лв.","availability_text":"IN_STOCK","variants":[{"value":"38"}],"images":["s.jpg"],"url":"https://stenso.net/p"}
    manufacturer={"model":"MARINE","manufacturer_code":"M1","en_iso":"20347","protection_class":"O2","slip_resistance":"SR","size_range":"35-50","weight":"640gr","technical_sections":{"UPPER":"Leather"},"tds_url":"https://panda/tds","images":["m.jpg"],"url":"https://pandasafety.com/product/marine/"}
    e=m.merged_evidence(supplier,manufacturer)
    assert e["commercial_truth"]["authority"]=="SUPPLIER"
    assert e["commercial_truth"]["price"]=="120 лв."
    assert e["technical_truth"]["authority"]=="MANUFACTURER"
    assert e["identity"]["supplier_reference"]=="S1"
    assert e["identity"]["manufacturer_code"]=="M1"

def test_supplier_gui_can_add_manufacturer_url():
    # Revision 18+ contract: Supplier Browser links to a separate manufacturer
    # page; it must not contain a nested manufacturer POST form.
    t=TEMPLATE.read_text(encoding="utf-8")
    assert "/supplier-browser/manufacturer-start?" in t
    assert "/supplier-browser/manufacturer-review" not in t
    assert "Добави производител + сравни" in t

    start = ROOT / "admin-platform/app/templates/supplier_browser/manufacturer_start.html"
    assert start.exists()
    s = start.read_text(encoding="utf-8")
    assert "/supplier-browser/manufacturer-review" in s
    assert 'name="manufacturer_url"' in s

def test_review_blocks_draft_pending_operator_identity_confirmation():
    t=REVIEW.read_text(encoding="utf-8")
    assert "DRAFT остава блокиран" in t
    assert "Supplier reference" in t
    assert "Manufacturer code" in t

def test_router_has_manufacturer_review_route():
    t=ROUTER.read_text(encoding="utf-8")
    assert '@router.post("/manufacturer-review")' in t
    assert "hydrate_manufacturer_product" in t
    assert "compare_identity" in t
