from pathlib import Path

def test_r4_handoff_does_not_hardcode_parent_prefix():
    t=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    assert '@router.get("/publish-handoff"' in t
    assert 'endswith("/r1-final")' in t
    assert 'publish_review_url=(f"/content-intelligence/publish-handoff?job_id=' in t

def test_r4_handoff_is_read_only_redirect_gate():
    t=Path("admin-platform/app/routers/phase46_r3_content_intelligence.py").read_text(encoding="utf-8")
    block=t.split('@router.get("/publish-handoff"',1)[1]
    assert 'RedirectResponse' in block
    assert 'status_code=303' in block
    assert '.commit(' not in block
    assert '.delete(' not in block
