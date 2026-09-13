from pathlib import Path
import ast
ROOT=Path(__file__).resolve().parents[1]
RO=(ROOT/"admin-platform/app/routers/phase46_r1_final_publish.py").read_text(encoding="utf-8")
TPL=(ROOT/"admin-platform/app/templates/operator_publish/phase46_r1_final.html").read_text(encoding="utf-8")
LIVE=(ROOT/"admin-platform/app/services/v073_phase46/canonical_live_pilot.py").read_text(encoding="utf-8")
STORE=(ROOT/"admin-platform/app/services/v073_phase46/secure_integration_settings.py").read_text(encoding="utf-8")
def test_integrated_settings_ui():
 for x in ("M99 Integration Settings",'type="password"',"SAVE IN M99","VERIFY m99.eu CONNECTION"):assert x in TPL
def test_superadmin_settings_routes():
 assert "/integration-settings/save" in RO and "/integration-settings/verify" in RO and "Integration Settings are Super Admin only." in RO
def test_live_publisher_uses_m99_credentials():
 assert "effective_m99eu_credentials()" in LIVE and "credential_source" in LIVE
def test_no_cmd_or_secret_rendering():
 for x in ("setx M99EU_API_KEY","echo %M99EU_API_KEY%","{{ integration_status.masked_api_key }}"):assert x not in TPL
def test_production_store_has_no_test_prefixed_function():
 tree=ast.parse(STORE);names=[n.name for n in tree.body if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef))];assert not any(n.startswith("test_") for n in names)
