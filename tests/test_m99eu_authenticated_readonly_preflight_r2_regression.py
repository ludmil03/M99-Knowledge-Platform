from pathlib import Path
import inspect
import integrations.m99eu_prestashop.readonly_preflight_r2 as p
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config
def test_authoritative_credential_name_preserved():assert "M99EU_PS_API_KEY" in inspect.getsource(load_m99eu_prestashop_config)
def test_transport_has_only_get_dispatch():
 s=inspect.getsource(p.OneShotBasicGetTransport)
 assert 'conn.request("GET"' in s
 for m in ("POST","PUT","PATCH","DELETE"):assert f'conn.request("{m}"' not in s
def test_no_retry_loop():assert "while " not in inspect.getsource(p.OneShotBasicGetTransport)
def test_exact_four_api_reads():
 s=inspect.getsource(p.run_preflight)
 for x in ('"/api"','"/api/languages"','"/api/categories/','"/api/products"'):assert x in s
def test_runner_import_bootstrap():
 t=(Path(__file__).resolve().parents[1]/"scripts/run_m99eu_authenticated_readonly_preflight_r2.py").read_text(encoding="utf-8-sig")
 assert "parents[1]" in t
