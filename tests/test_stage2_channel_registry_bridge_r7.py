from app.services.channel_registry_bridge import available_governed_targets, resolve_governed_target_scope

def test_toplinka_visible_authorized_not_ready():
    t = {x.key: x for x in available_governed_targets()}["toplinka.com"]
    assert t.authorized is True
    assert t.ready is False
    assert t.platform == "WordPress + WooCommerce"
    s = resolve_governed_target_scope(["toplinka.com"])
    assert s["authorized_targets"] == ["toplinka.com"]
    assert s["ready_targets"] == []
    assert s["blocked_targets"] == ["toplinka.com"]

def test_m99eu_remains_ready():
    s = resolve_governed_target_scope(["m99.eu"])
    assert s["ready_targets"] == ["m99.eu"]

def test_unknown_target_fails_closed():
    s = resolve_governed_target_scope(["unknown.example"])
    assert s["authorized_targets"] == []
    assert s["ready_targets"] == []
    assert s["blocked_targets"] == ["unknown.example"]

def test_mixed_scope_deduplicates_and_intersects():
    s = resolve_governed_target_scope(["m99.eu", "toplinka.com", "m99.eu", "alviro.ro"])
    assert s["requested_targets"] == ["m99.eu", "toplinka.com", "alviro.ro"]
    assert s["authorized_targets"] == ["m99.eu", "toplinka.com", "alviro.ro"]
    assert s["ready_targets"] == ["m99.eu"]
    assert s["blocked_targets"] == ["toplinka.com", "alviro.ro"]
