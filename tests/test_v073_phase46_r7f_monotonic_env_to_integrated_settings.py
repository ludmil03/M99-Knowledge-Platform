
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SVC=(ROOT/"admin-platform/app/services/v073_phase46/canonical_live_pilot.py").read_text(encoding="utf-8")
SETTINGS=(ROOT/"admin-platform/app/services/v073_phase46/secure_integration_settings.py").read_text(encoding="utf-8")
ROUTER=(ROOT/"admin-platform/app/routers/phase46_r1_final_publish.py").read_text(encoding="utf-8")
TPL=(ROOT/"admin-platform/app/templates/operator_publish/phase46_r1_final.html").read_text(encoding="utf-8")

def test_env_only_gate_is_replaced_not_removed():
    import ast
    tree=ast.parse(SVC)
    assert "effective_m99eu_credentials()" in SVC
    assert "PUBLISH CANONICAL PILOT TO M99.EU" in SVC
    assert 'str(confirmation or "").strip()!=CONFIRMATION' in SVC
    assert 'getattr(user,"is_superuser",False)' in SVC
    assert 'tag("active","0")' in SVC
    assert 'tag("available_for_order","0")' in SVC
    assert 'tag("visibility","none")' in SVC

    pairs=[
        (ast.unparse(node.test),ast.unparse(node))
        for node in ast.walk(tree)
        if isinstance(node,ast.If)
    ]
    assert any(cond=="not enabled" and "CanonicalPilotError" in body for cond,body in pairs)
    assert any("re.fullmatch" in cond and "api_key" in cond and "CanonicalPilotError" in body for cond,body in pairs)

def test_integrated_settings_are_secure_and_env_is_fallback_only():
    assert "WINDOWS_DPAPI_CURRENT_USER" in SETTINGS
    assert "LEGACY_ENV_FALLBACK" in SETTINGS
    assert "M99_SECURE_SETTINGS" in SETTINGS
    assert "CryptProtectData" in SETTINGS
    assert "CryptUnprotectData" in SETTINGS

def test_operator_control_is_inside_m99_without_secret_echo():
    assert "/integration-settings/save" in ROUTER
    assert "/integration-settings/verify" in ROUTER
    assert "Integration Settings are Super Admin only." in ROUTER
    assert "M99 Integration Settings — m99.eu" in TPL
    assert 'type="password"' in TPL
    assert "SAVE IN M99" in TPL
    assert "VERIFY m99.eu CONNECTION" in TPL
    assert "setx M99EU_API_KEY" not in TPL
