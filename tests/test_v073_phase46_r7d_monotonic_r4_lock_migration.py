from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROUTER=(ROOT/'admin-platform/app/routers/phase46_r1_final_publish.py').read_text(encoding='utf-8')
SVC=(ROOT/'admin-platform/app/services/v073_phase46/canonical_live_pilot.py').read_text(encoding='utf-8')
TPL=(ROOT/'admin-platform/app/templates/operator_publish/phase46_r1_final.html').read_text(encoding='utf-8')

def test_old_preview_only_lock_is_replaced_by_stronger_conditional_gate_not_removed():
    for x in ('publish_canonical_pilot','payload_preview = build_canonical_payload_preview'):
        assert x in ROUTER
    for x in ('M99EU_CANONICAL_PILOT_ENABLED','PUBLISH CANONICAL PILOT TO M99.EU',
              'Super Admin only','Job must remain DRAFT for first pilot',
              'Job is not requested+authorized for m99.eu','Canonical Payload Preview is not READY'):
        assert x in SVC
    assert 'PUBLISH BLOCKED — CANONICAL PREVIEW NOT READY' in TPL

def test_safe_hidden_state_duplicate_guard_readback_remain_hard_contracts():
    for x in ('tag("active","0")','tag("available_for_order","0")','tag("visibility","none")',
              'Duplicate guard found an existing product that is not the exact safe hidden pilot state',
              'Readback mismatch'):
        assert x in SVC
