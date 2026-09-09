from pathlib import Path

def test_application_contract_still_present():
    repo=Path(__file__).resolve().parents[1]
    admin=repo/"admin-platform"
    assert (admin/"app/routers/phase46_r3_content_intelligence.py").exists()
    assert (admin/"app/services/v073_phase46/content_manufacturer_intelligence.py").exists()
