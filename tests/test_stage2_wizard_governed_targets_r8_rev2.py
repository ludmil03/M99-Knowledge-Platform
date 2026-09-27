from app.services.product_import_wizard import available_targets, resolve_target_scope
def test_toplinka():
    t={x.key:x for x in available_targets()}["toplinka.com"]
    assert t.authorized and not t.ready
    s=resolve_target_scope(["toplinka.com"])
    assert s["authorized_targets"]==["toplinka.com"] and s["ready_targets"]==[]
def test_ready_unknown():
    assert resolve_target_scope(["m99.eu"])["ready_targets"]==["m99.eu"]
    assert resolve_target_scope(["unknown.example"])["blocked_targets"]==["unknown.example"]
