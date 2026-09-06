from types import SimpleNamespace

from app.services.v073_phase45.m99eu_operator_single_publish import candidate_from_item, provisional_reference


def test_candidate_extracts_hydrated_fields():
    item = SimpleNamespace(
        id=17,
        source_snapshot_json='{"title":"Real Shoe","supplier_reference":"ABC-17","price":"149.99","description":"Evidence text","source_url":"https://supplier/item"}'
    )
    c = candidate_from_item(item)
    assert c.item_id == 17
    assert c.title == "Real Shoe"
    assert c.supplier_reference == "ABC-17"
    assert c.price == "149.99"
    assert c.publishable is True
    assert c.provisional_m99_reference == provisional_reference(17)
    assert c.provisional_m99_reference.startswith("M99-")
    assert c.provisional_m99_reference[4:].isdigit()


def test_candidate_blocks_missing_required_hydration():
    item = SimpleNamespace(id=18, source_snapshot_json='{"title":"Only title"}')
    c = candidate_from_item(item)
    assert c.publishable is False
    assert any("supplier reference" in b.lower() for b in c.blockers)
    assert any("price" in b.lower() for b in c.blockers)
