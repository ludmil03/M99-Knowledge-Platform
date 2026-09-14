from types import SimpleNamespace


def _supplier():
    return {
        "url":"https://palltex.bg/bg/p/leten-raboten-pantalon-daytona-trousers-antracit-cvqt/17374",
        "name":"Летен работен панталон BWOLF DAYTONA Trousers <br>Антрацит цвят",
        "title":"Летен работен панталон BWOLF DAYTONA Trousers <br>Антрацит цвят",
        "supplier_reference":"042554",
        "brand":"BWOLF",
        "description":"Работен панталон DAYTONA. Cross-selling text may mention риза, but identity remains trousers.",
        "images":["https://palltex.bg/daytona.png"],
        "variants":[{"type":"COLOR_SIZE","value":"Антрацит","sizes":[{"size":x,"availability":"INSTOCK"} for x in ("XS","S","M","L","XL","2XL","3XL","4XL")]}],
    }


def _manufacturer():
    return {
        "status":"OPERATOR_CONFIRMED_EXACT",
        "official_site":"https://palltex.bg",
        "official_product_url":"https://palltex.bg/bg/p/leten-raboten-pantalon-daytona-trousers-antracit-cvqt/17374",
        "manufacturer_product_code":"042554",
        "manufacturer_product_code_status":"VERIFIED_EXACT_REFERENCE",
        "page_title":"BWOLF DAYTONA trousers 042554",
        "images":["https://palltex.bg/daytona.png"],
        "documents":[],"tables":[],"text_excerpt":"DAYTONA trousers 042554",
    }


def test_current_generator_title_first_trousers_and_no_raw_br():
    from app.services.v073_phase46.content_manufacturer_intelligence import build_content_bundle
    b=build_content_bundle(supplier_evidence=_supplier(),manufacturer_evidence=_manufacturer(),target_code="m99eu")
    assert set(b["documents"])=={"EN","BG","RU"}
    for code,d in b["documents"].items():
        flat=" ".join(str(d.get(k) or "") for k in ("product_name","h1","short_description","meta_title","meta_description","long_description_html")).lower()
        assert "<br>" not in " ".join(str(d.get(k) or "") for k in ("product_name","h1","short_description","meta_title","meta_description")).lower()
        assert "professional shirt" not in flat
        assert "мъжка риза" not in flat
        assert "женская рубашка" not in flat


def test_publish_gate_passes_rebuilt_daytona_bundle():
    from app.services.v073_phase46.content_manufacturer_intelligence import build_content_bundle
    from app.services.v073_phase46.publish_ready_content_gate import validate_publish_ready_content
    b=build_content_bundle(supplier_evidence=_supplier(),manufacturer_evidence=_manufacturer(),target_code="m99eu")
    g=validate_publish_ready_content(supplier_title=_supplier()["title"],supplier_description=_supplier()["description"],languages=b["documents"])
    assert g["source_type"]=="trousers"
    assert g["pass"] is True, g["blockers"]


def test_live_pilot_accepts_normative_identity_surface():
    from app.services.v073_phase46.canonical_live_pilot import validate_preview
    docs={}
    for code in ("EN","BG","RU"):
        docs[code]={"product_name":"DAYTONA trousers","h1":"DAYTONA trousers","short_description":"Verified trousers.","long_description_html":"<h2>Details</h2><p>Verified trousers.</p>","meta_title":"DAYTONA trousers","meta_description":"Verified DAYTONA trousers details.","manufacturer_reference_in_specs":"042554"}
    preview={"ready":True,"status":"READY","identifiers":{"channel_reference":"M99 100018","channel_reference_role":"PERMANENT_M99_REFERENCE","supplier_reference_role":"SUPPLIER_MAPPING_ONLY","manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY","manufacturer_reference":"042554"},"languages":docs,"images":{"count":1},"variants":{"rows_count":8}}
    validate_preview(preview)


def test_bridge_rebuilds_even_same_job_content(monkeypatch):
    from app.services.v073_phase46 import r4_r1_canonical_payload_bridge as b
    supplier=_supplier(); manufacturer=_manufacturer()
    stale={"languages":["EN","BG","RU"],"documents":{"EN":{"product_name":"A professional shirt"},"BG":{"product_name":"Мъжка риза"},"RU":{"product_name":"Рубашка"}},"identifier_governance":{"supplier_reference_role":"SUPPLIER_MAPPING_ONLY","manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY"}}
    durable={"job_id":26,"item_id":99,"target":"m99eu","supplier_reference":"042554","supplier_evidence":supplier,"manufacturer_evidence":manufacturer,"content_bundle":stale,"payload_sha256":"abc"}
    monkeypatch.setattr(b,"load_enrichment",lambda job_id:durable)
    monkeypatch.setattr(b,"canonical_reference_from_draft",lambda **kw:"M99 100018")
    job=SimpleNamespace(id=26); item=SimpleNamespace(id=99,supplier_reference="042554",source_url=supplier["url"],source_title=supplier["title"])
    out=b.build_canonical_payload_preview(job=job,item=item)
    assert out["ready"] is True, out["blockers"]
    assert out["publish_ready_content_gate"]["pass"] is True
    assert out["durable_source_mode"]=="SAME_JOB"
    assert "shirt" not in out["languages"]["EN"]["product_name"].lower()
