from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import pytest

R37_ROUTER = Path("admin-platform/app/routers/r37_add_products_flow.py")
R37_PREP = Path("admin-platform/app/templates/add_products/r37_prepare.html")
OPERATOR_ROUTER = Path("admin-platform/app/routers/operator_single_product_publish.py")
PHASE46_ROUTER = Path("admin-platform/app/routers/phase46_r1_final_publish.py")


def test_frozen_r37_router_still_has_no_publish_write():
    text = R37_ROUTER.read_text(encoding="utf-8").lower()
    assert "publish" not in text


def test_frozen_r37_prepare_contract_preserved():
    text = R37_PREP.read_text(encoding="utf-8")
    assert "{% if bridge.bridge_ready %}" in text
    assert "Потвърди Identity и създай DRAFT" in text


def test_phase46_is_separate_control_plane():
    text = PHASE46_ROUTER.read_text(encoding="utf-8")
    assert 'APIRouter(prefix="/r1-final"' in text
    assert "publish_existing_draft_job" in text
    operator = OPERATOR_ROUTER.read_text(encoding="utf-8")
    assert "M99_PHASE46_R1_FINAL_INCLUDE" in operator
    assert "phase46_r1_final_publish" in operator


def test_phase46_constants():
    from app.services.v073_phase45 import m99eu_r37_auto_publish as s
    assert s.DEFAULT_CATEGORY_ID == 26
    assert s.R1_CONFIRMATION == "PUBLISH ONE PRODUCT"
    assert s.PILOT_ACTIVE == "1"
    assert s.PILOT_AVAILABLE_FOR_ORDER == "0"
    assert s.PILOT_VISIBILITY == "none"


def test_config_requires_explicit_enable(monkeypatch):
    from app.services.v073_phase45.m99eu_r37_auto_publish import AutoPublishError, load_config
    monkeypatch.delenv("M99EU_AUTO_PUBLISH_ENABLED", raising=False)
    monkeypatch.setenv("M99EU_API_KEY", "A" * 32)
    with pytest.raises(AutoPublishError):
        load_config(26)


def test_draft_reference_no_provisional_fallback():
    from app.services.v073_phase45.m99eu_r37_auto_publish import (
        AutoPublishError,
        canonical_reference_from_draft,
    )
    job = SimpleNamespace()
    item = SimpleNamespace(detection={"reference": "SUP-1"})
    with pytest.raises(AutoPublishError, match="permanent canonical"):
        canonical_reference_from_draft(job=job, item=item)

    item = SimpleNamespace(detection={"identity": {"m99_reference": "M99-12345"}})
    assert canonical_reference_from_draft(job=job, item=item) == "M99-12345"


def test_supplier_snapshot_extracts_price_from_detection():
    from app.services.v073_phase45.m99eu_r37_auto_publish import supplier_product_from_draft_item
    item = SimpleNamespace(
        source_title="Pilot",
        supplier_reference="SUP-1",
        source_url="https://supplier.invalid/1",
        detection={"commercial": {"price_text": "19,99 EUR"}},
    )
    p = supplier_product_from_draft_item(item)
    assert p["title"] == "Pilot"
    assert p["supplier_reference"] == "SUP-1"
    assert p["price_text"] == "19,99 EUR"


def test_candidate_uses_only_permanent_reference():
    from app.services.v073_phase45.m99eu_r37_auto_publish import candidate_from_supplier_product
    item = SimpleNamespace(id=7, source_title="Pilot", supplier_reference="SUP-7", source_url="https://x.invalid")
    c = candidate_from_supplier_product(
        item,
        {"title":"Pilot","supplier_reference":"SUP-7","price_text":"20.00 EUR","url":"https://x.invalid"},
        canonical_reference="M99-7007",
    )
    assert c.publishable is True
    assert c.provisional_m99_reference == "M99-7007"


def test_hidden_active_pilot_payload(monkeypatch):
    from app.services.v073_phase45 import m99eu_r37_auto_publish as s
    from app.services.v073_phase45.m99eu_operator_single_publish import Candidate
    monkeypatch.setattr(s, "build_payload", lambda *a, **k: (
        "<product><active><![CDATA[0]]></active>"
        "<available_for_order><![CDATA[0]]></available_for_order>"
        "<visibility><![CDATA[none]]></visibility></product>"
    ))
    c=Candidate(item_id=1,title="Pilot",supplier_reference="SUP-1",price="12.34",description="",source_url="",provisional_m99_reference="M99-1",publishable=True,blockers=())
    x=s._pilot_payload(c,26,[("1","en")])
    assert "<active><![CDATA[1]]></active>" in x
    assert "<available_for_order><![CDATA[0]]></available_for_order>" in x
    assert "<visibility><![CDATA[none]]></visibility>" in x
