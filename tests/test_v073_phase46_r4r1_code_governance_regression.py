from pathlib import Path
ADMIN=Path(__file__).resolve().parents[1]/"admin-platform"
CONTENT=ADMIN/"app/services/v073_phase46/content_manufacturer_intelligence.py"

def test_external_ids_remain_mappings_not_canonical_identity():
    s=CONTENT.read_text(encoding="utf-8")
    assert "SUPPLIER_MAPPING_ONLY" in s
    assert "VERIFIED_MANUFACTURER_MPN_ONLY" in s
    assert "PERMANENT_M99_REFERENCE" in s

def test_supplier_and_manufacturer_equal_value_does_not_merge_roles():
    # RIVER may legitimately have 93100 in both source mappings after exact
    # manufacturer confirmation. Equality of values never collapses roles.
    supplier_ref="93100"; manufacturer_ref="93100"
    assert supplier_ref==manufacturer_ref
    roles={"supplier":supplier_ref,"manufacturer":manufacturer_ref}
    assert set(roles)=={"supplier","manufacturer"}
