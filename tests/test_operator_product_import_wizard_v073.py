from pathlib import Path
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
ADMIN = ROOT / "admin-platform"
if str(ADMIN) not in sys.path:
    sys.path.insert(0, str(ADMIN))

from app.services.product_import_wizard import (
    ImportWizardDraft,
    ProposalStatus,
    SelectionMode,
    approved_organizations,
    available_targets,
    build_review_summary,
    propose_organization,
    resolve_target_scope,
    selection_modes,
    validate_selection,
)


def test_operator_wizard_supports_all_decided_selection_modes():
    modes = {x["value"] for x in selection_modes()}
    assert SelectionMode.ONE_PRODUCT.value in modes
    assert SelectionMode.MULTIPLE_PRODUCTS.value in modes
    assert SelectionMode.ONE_CATEGORY.value in modes
    assert SelectionMode.MULTIPLE_CATEGORIES.value in modes
    assert SelectionMode.ALL_PRODUCTS.value in modes
    assert SelectionMode.FIRST_N.value in modes
    assert SelectionMode.ONLY_NEW_TO_M99.value in modes
    assert SelectionMode.MANUAL_SELECTION.value in modes


def test_one_product_requires_exactly_one_product():
    validate_selection("one_product", ["A"], [], None)
    with pytest.raises(ValueError):
        validate_selection("one_product", ["A", "B"], [], None)


def test_multiple_products_requires_two_or_more():
    validate_selection("multiple_products", ["A", "B"], [], None)
    with pytest.raises(ValueError):
        validate_selection("multiple_products", ["A"], [], None)


def test_multiple_categories_requires_two_or_more():
    validate_selection("multiple_categories", [], ["CAT-A", "CAT-B"], None)
    with pytest.raises(ValueError):
        validate_selection("multiple_categories", [], ["CAT-A"], None)


def test_first_n_requires_positive_number():
    validate_selection("first_n", [], [], 20)
    with pytest.raises(ValueError):
        validate_selection("first_n", [], [], 0)


def test_operator_can_propose_supplier_and_manufacturer_but_not_auto_approve():
    proposal = propose_organization("New Org", ["SUPPLIER", "MANUFACTURER"])
    assert proposal["status"] == ProposalStatus.PENDING_SUPER_ADMIN_APPROVAL.value
    assert proposal["visible_to_operators"] is False


def test_approved_organizations_only_are_listed():
    assert approved_organizations()
    assert all(org.approved for org in approved_organizations())


def test_m99eu_is_only_one_of_multiple_targets():
    keys = [x.key for x in available_targets()]
    assert "m99.eu" in keys
    assert len(keys) > 3


def test_target_scope_is_requested_authorized_ready_intersection():
    scope = resolve_target_scope(["m99.eu", "alviro.ro", "toplinka.com"])
    assert scope["requested_targets"] == ["m99.eu", "alviro.ro", "toplinka.com"]
    assert "m99.eu" in scope["authorized_targets"]
    assert "m99.eu" in scope["ready_targets"]
    assert "alviro.ro" in scope["blocked_targets"]
    assert "toplinka.com" in scope["blocked_targets"]


def test_review_summary_performs_no_write():
    draft = ImportWizardDraft(
        source_name="STENSO",
        selection_mode="multiple_products",
        selected_product_refs=["A", "B"],
        requested_targets=["m99.eu", "mela99.com"],
        authorized_targets=["m99.eu", "mela99.com"],
        ready_targets=["m99.eu", "mela99.com"],
    )
    summary = build_review_summary(draft)
    assert summary["can_continue"] is True
    assert summary["write_performed"] is False


def test_router_and_template_use_generalized_add_products_not_m99eu_only():
    router = (ADMIN / "app/routers/product_import_wizard.py").read_text(encoding="utf-8-sig")
    template = (ADMIN / "app/templates/product_import_wizard/wizard.html").read_text(encoding="utf-8-sig")
    assert 'prefix="/operator/add-products"' in router
    assert "Добави продукти" in template
    assert "m99.eu" not in template or "targets" in template.lower()


def test_router_has_no_product_write_call():
    router = (ADMIN / "app/routers/product_import_wizard.py").read_text(encoding="utf-8-sig")
    service = (ADMIN / "app/services/product_import_wizard.py").read_text(encoding="utf-8-sig")
    forbidden = (
        "create_product(",
        "requests.post(",
        "client.create_product",
        "/api/products",
    )
    for token in forbidden:
        assert token not in router
        assert token not in service


def test_architecture_declares_no_write_foundation():
    text = (ROOT / "ARCHITECTURE_v0.7.3.md").read_text(encoding="utf-8-sig")
    assert "NO product write" in text
    assert "m99.eu is only one target" in text
    assert "PENDING_SUPER_ADMIN_APPROVAL" in text
