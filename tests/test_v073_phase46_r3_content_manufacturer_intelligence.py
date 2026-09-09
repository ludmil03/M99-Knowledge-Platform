from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SVC=ROOT/"admin-platform/app/services/v073_phase46/content_manufacturer_intelligence.py"
ROUTER=ROOT/"admin-platform/app/routers/phase46_r3_content_intelligence.py"
AGG=ROOT/"admin-platform/app/routers/operator_single_product_publish.py"
CANON=ROOT/"admin-platform/app/templates/add_products/r37_canonical_preview.html"

def test_language_policy_and_benchmarks():
    s=SVC.read_text(encoding="utf-8")
    assert '"m99eu":("EN","BG","RU")' in s
    for x in ("Amazon","Zalando","eBay","Apple"): assert x in s

def test_schema_adaptive_persistence_contract():
    s=SVC.read_text(encoding="utf-8")
    assert 'required=("id","import_job_id","selected")' in s
    assert 'carrier="detection" if hasattr(ImportJobItem,"detection") else None' in s
    assert '"NO_MAPPED_DRAFT_EVIDENCE_CARRIER"' in s
    assert "product_for_canonical_preview_from_draft" in s

def test_source_context_is_carried_from_canonical_preview():
    c=CANON.read_text(encoding="utf-8")
    assert "source_uuid=" in c and "product_url=" in c
    r=ROUTER.read_text(encoding="utf-8")
    assert "source_uuid:str" in r and "product_url:str" in r
    assert "draft_context(db,job_id,source_uuid,product_url)" in r

def test_no_channel_write_in_r3():
    b=(SVC.read_text(encoding="utf-8")+ROUTER.read_text(encoding="utf-8")).lower()
    assert "requests.post" not in b
    assert "/api/products" not in b
    assert "authorization: basic" not in b

def test_ssrf_and_confirmation():
    s=SVC.read_text(encoding="utf-8")
    assert "ip.is_private" in s and "ip.is_loopback" in s
    assert "CONFIRM EXACT MANUFACTURER PRODUCT" in ROUTER.read_text(encoding="utf-8")

def test_content_components():
    s=SVC.read_text(encoding="utf-8")
    for x in ("meta_title","meta_description","technical_specifications","faq","image_alt","schema_product"):
        assert x in s
    assert '"H2"' in s and '"H3"' in s

def test_registration_and_frozen_r37():
    assert "phase46_r3_content_router" in AGG.read_text(encoding="utf-8")
    r=(ROOT/"admin-platform/app/routers/r37_add_products_flow.py").read_text(encoding="utf-8").lower()
    assert "publish" not in r


def test_fix8_manufacturer_auto_resolution_and_unknown_are_supported():
    s=SVC.read_text(encoding="utf-8")
    assert "def resolve_manufacturer_source" in s
    assert '"status":"UNKNOWN"' in s
    assert '"status":"KNOWN"' in s
    assert 'approved_sources(db,kind="MANUFACTURER")' in s
    assert "SequenceMatcher" in s

def test_fix8_manufacturer_code_is_not_manual_input():
    s=SVC.read_text(encoding="utf-8")
    assert "def resolve_manufacturer_product_code" in s
    assert '"CANDIDATE_FROM_SUPPLIER_REFERENCE"' in s
    assert '"VERIFIED_EXACT_REFERENCE"' in s
    t=(ROOT/"admin-platform/app/templates/content_intelligence/review.html").read_text(encoding="utf-8")
    assert 'name="manufacturer_product_code"' not in t
    assert "manufacturer_product_code.code" in t

def test_fix8_discover_does_not_raise_raw_500_for_runtime_failures():
    r=ROUTER.read_text(encoding="utf-8")
    discover_block=r.split('@router.post("/discover"',1)[1].split('@router.post("/confirm"',1)[0]
    assert 'manufacturer_site_url:str=Form("")' in discover_block
    assert "except Exception as exc:" in discover_block
    assert "Manufacturer discovery failed safely:" in discover_block
    assert "raise HTTPException(409" not in discover_block

def test_fix8_direct_product_url_is_checked_first():
    s=SVC.read_text(encoding="utf-8")
    assert "seed_url" in s
    assert "queue=[" in s
    assert "u==seed_url" in s

def test_fix8_known_manufacturer_uses_hidden_approved_site_and_manual_is_advanced():
    t=(ROOT/"admin-platform/app/templates/content_intelligence/review.html").read_text(encoding="utf-8")
    assert 'manufacturer_source.status == "KNOWN"' in t
    assert 'type="hidden" name="manufacturer_site_url" value="{{ manufacturer_source.official_site }}"' in t
    assert "Advanced: manual official-site override" in t
    assert "Manufacturer: <b>UNKNOWN</b>" in t


def test_fix10_discovery_queue_normalizes_sitemap_tuple_before_composition():
    s=SVC.read_text(encoding="utf-8")
    assert "sitemap_urls=list(_sitemap(site,fetch,supplier_reference,title_hint) or ())" in s
    assert "*sitemap_urls" in s
    assert "] + _sitemap(" not in s
    assert "queue=list(dict.fromkeys(str(x) for x in queue if x))" in s


def test_fix11_manufacturer_supplier_sequence_merges_are_type_normalized():
    s=SVC.read_text(encoding="utf-8")
    assert '[*list(m.get("images") or ()),*list(s.get("images") or ())]' in s
    assert '(m.get("images") or [])+(s.get("images") or [])' not in s
    assert 'list(m.get("tables") or ())' in s
