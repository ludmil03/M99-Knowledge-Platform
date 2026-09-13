from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ROUTER=ROOT/'admin-platform/app/routers/phase46_r1_final_publish.py'
TPL=ROOT/'admin-platform/app/templates/operator_publish/phase46_r1_final.html'
SVC=ROOT/'admin-platform/app/services/v073_phase46/canonical_live_pilot.py'

def test_router_uses_canonical_pilot_not_legacy_publish_call():
    s=ROUTER.read_text(encoding='utf-8')
    assert 'publish_canonical_pilot' in s
    assert 'publish_existing_draft_job(' not in s
    assert 'price_override' in s

def test_default_server_state_is_locked_until_integrated_settings_and_exact_confirmation():
    import ast
    source=SVC.read_text(encoding='utf-8')
    tree=ast.parse(source)

    assert 'PUBLISH CANONICAL PILOT TO M99.EU' in source
    assert 'effective_m99eu_credentials()' in source
    assert 'str(confirmation or "").strip()!=CONFIRMATION' in source

    pairs=[
        (ast.unparse(node.test),ast.unparse(node))
        for node in ast.walk(tree)
        if isinstance(node,ast.If)
    ]
    assert any(cond=="not enabled" and "CanonicalPilotError" in body for cond,body in pairs)
    assert any("re.fullmatch" in cond and "api_key" in cond and "CanonicalPilotError" in body for cond,body in pairs)

    settings=(ROOT/'admin-platform/app/services/v073_phase46/secure_integration_settings.py').read_text(encoding='utf-8')
    for x in ('WINDOWS_DPAPI_CURRENT_USER','LEGACY_ENV_FALLBACK','verify_m99eu_connection'):
        assert x in settings
