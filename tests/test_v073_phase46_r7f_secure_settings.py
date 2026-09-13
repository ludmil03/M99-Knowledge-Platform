from pathlib import Path
import json,sys,pytest
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.secure_integration_settings import SecureSettingsError,save_m99eu_settings,load_m99eu_secret,public_m99eu_status,settings_path

def protect(b):return b"ENC:"+b[::-1]
def unprotect(b):assert b.startswith(b"ENC:");return b[4:][::-1]
def test_save_encrypts_and_reloads_without_restart(tmp_path):
 key="A"*32;st=save_m99eu_settings(api_key=key,enabled=True,repo_root=tmp_path,protect=protect)
 raw=settings_path(tmp_path).read_text(encoding="utf-8");assert key not in raw
 assert st["configured"] and st["enabled"] and st["restart_required"] is False
 assert load_m99eu_secret(repo_root=tmp_path,unprotect=unprotect)==key
def test_blank_key_keeps_ciphertext(tmp_path):
 save_m99eu_settings(api_key="B"*32,enabled=False,repo_root=tmp_path,protect=protect);before=json.loads(settings_path(tmp_path).read_text(encoding="utf-8"))
 save_m99eu_settings(api_key="",enabled=True,repo_root=tmp_path,protect=protect);after=json.loads(settings_path(tmp_path).read_text(encoding="utf-8"))
 assert before["api_key_dpapi_b64"]==after["api_key_dpapi_b64"] and after["enabled"] is True
def test_invalid_key_blocks(tmp_path):
 with pytest.raises(SecureSettingsError):save_m99eu_settings(api_key="bad",enabled=True,repo_root=tmp_path,protect=protect)
def test_runtime_path_contract_is_outside_repo():
 p=str(settings_path()).replace("\\","/");assert "M99KnowledgePlatform/secure-settings/m99eu.json" in p and "admin-platform" not in p
def test_no_production_helper_named_test():
 import app.services.v073_phase46.secure_integration_settings as m
 names=[n for n,v in vars(m).items() if callable(v) and not n.startswith("_")]
 assert "test_m99eu_connection" not in names and "verify_m99eu_connection" in names
