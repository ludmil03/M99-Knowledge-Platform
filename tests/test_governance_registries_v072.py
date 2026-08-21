from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
GOV = ROOT / "governance"


def read(name: str) -> str:
    return (GOV / name).read_text(encoding="utf-8-sig")


def test_required_governance_files_exist():
    for name in (
        "DECISION_REGISTRY.yaml",
        "FEATURE_GAP_REGISTRY.yaml",
        "M99_CURRENT_CONTEXT.yaml",
    ):
        assert (GOV / name).is_file(), name


def test_decision_registry_contains_core_anti_loop_rules():
    text = read("DECISION_REGISTRY.yaml")
    assert 'anti_loop_rule: "DECIDED != IMPLEMENTED"' in text
    assert "A failed implementation attempt does not reopen a DECIDED rule." in text
    assert "m99.eu is one target channel, not the central Add Product workflow." in text


def test_decision_ids_are_unique():
    text = read("DECISION_REGISTRY.yaml")
    ids = re.findall(r"^\s*-\s+id:\s+([A-Z0-9-]+)\s*$", text, flags=re.MULTILINE)
    assert ids
    assert len(ids) == len(set(ids))


def test_feature_registry_separates_normative_and_implementation_status():
    text = read("FEATURE_GAP_REGISTRY.yaml")
    assert "normative_status:" in text
    assert "implementation_status:" in text
    assert "generalized_add_products_wizard" in text
    assert "m99eu_dedicated_admin_screen" in text
    assert "normative_status: SUPERSEDED" in text


def test_current_context_points_to_readme_v8():
    text = read("M99_CURRENT_CONTEXT.yaml")
    assert "master_readme: README_v8.md" in text
    assert 'next_target: "v0.7.3 - Operator Product Import Wizard Foundation"' in text


def test_current_context_contains_multi_channel_operator_scope():
    text = read("M99_CURRENT_CONTEXT.yaml")
    assert "one_product" in text
    assert "multiple_products" in text
    assert "one_category" in text
    assert "multiple_categories" in text
    assert "all_products_where_supported" in text
    assert "one_or_many_authorized_channels_and_or_erp" in text


def test_current_context_contains_m99eu_verified_state():
    text = read("M99_CURRENT_CONTEXT.yaml")
    assert 'platform: "PrestaShop 9.1.5"' in text
    assert '"1": EN' in text
    assert '"2": BG' in text
    assert '"3": RU' in text
    assert "test_category_id: 26" in text
    assert "dry_run: PASS" in text


def test_org_approval_rule_is_preserved():
    text = read("DECISION_REGISTRY.yaml")
    assert "New Supplier, Manufacturer and Brand proposals require Super Admin approval" in text


def test_readme_v8_exists_and_mentions_registries():
    text = (ROOT / "README_v8.md").read_text(encoding="utf-8-sig")
    assert "DECISION_REGISTRY.yaml" in text
    assert "FEATURE_GAP_REGISTRY.yaml" in text
    assert "M99_CURRENT_CONTEXT.yaml" in text


def test_adr_exists_and_is_accepted():
    path = ROOT / "docs/ADR/ADR-0001-anti-loop-project-governance.md"
    text = path.read_text(encoding="utf-8-sig")
    assert "ACCEPTED" in text
    assert "failed implementation does not reopen" in text.lower()
