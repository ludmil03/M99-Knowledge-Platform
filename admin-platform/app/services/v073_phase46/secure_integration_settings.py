from __future__ import annotations
import base64,ctypes,json,os,re,tempfile
from urllib.parse import urlparse
from ctypes import wintypes
from pathlib import Path
from typing import Callable
INTEGRATION_ID="m99eu";KEY_RE=re.compile(r"^[A-Za-z0-9]{32}$");SCHEMA="m99.integrations.secure_settings.v3"
class SecureSettingsError(RuntimeError):pass
class DATA_BLOB(ctypes.Structure):_fields_=[("cbData",wintypes.DWORD),("pbData",ctypes.POINTER(ctypes.c_byte))]
def _blob(data:bytes):
 b=ctypes.create_string_buffer(data);return DATA_BLOB(len(data),ctypes.cast(b,ctypes.POINTER(ctypes.c_byte))),b
def _dpapi_protect(data:bytes)->bytes:
 if os.name!="nt":raise SecureSettingsError("Windows DPAPI is required for production secret persistence.")
 crypt32=ctypes.windll.crypt32;kernel32=ctypes.windll.kernel32;ib,buf=_blob(data);ob=DATA_BLOB()
 if not crypt32.CryptProtectData(ctypes.byref(ib),"M99 Knowledge Platform",None,None,None,0x1,ctypes.byref(ob)):raise SecureSettingsError("Windows DPAPI failed to encrypt integration secret.")
 try:return ctypes.string_at(ob.pbData,ob.cbData)
 finally:kernel32.LocalFree(ob.pbData)
def _dpapi_unprotect(data:bytes)->bytes:
 if os.name!="nt":raise SecureSettingsError("Windows DPAPI is required for production secret persistence.")
 crypt32=ctypes.windll.crypt32;kernel32=ctypes.windll.kernel32;ib,buf=_blob(data);ob=DATA_BLOB()
 if not crypt32.CryptUnprotectData(ctypes.byref(ib),None,None,None,None,0x1,ctypes.byref(ob)):raise SecureSettingsError("Windows DPAPI failed to decrypt integration secret.")
 try:return ctypes.string_at(ob.pbData,ob.cbData)
 finally:kernel32.LocalFree(ob.pbData)
def settings_path(repo_root=None):
 if repo_root is not None:return Path(repo_root)/"m99eu.json"
 local=os.environ.get("LOCALAPPDATA","").strip()
 base=Path(local) if local else Path.home()/"AppData"/"Local"
 return base/"M99KnowledgePlatform"/"secure-settings"/"m99eu.json"
def _atomic_write(path:Path,text:str):
 path.parent.mkdir(parents=True,exist_ok=True);fd,name=tempfile.mkstemp(prefix=".m99eu-",suffix=".tmp",dir=str(path.parent));tmp=Path(name)
 try:
  with os.fdopen(fd,"w",encoding="utf-8",newline="\n") as f:f.write(text);f.flush();os.fsync(f.fileno())
  try:os.chmod(tmp,0o600)
  except OSError:pass
  os.replace(tmp,path)
  try:os.chmod(path,0o600)
  except OSError:pass
 finally:
  if tmp.exists():tmp.unlink(missing_ok=True)
def _read_raw(repo_root=None):
 p=settings_path(repo_root)
 if not p.is_file():return {}
 try:d=json.loads(p.read_text(encoding="utf-8"))
 except Exception as e:raise SecureSettingsError("Stored m99.eu integration settings are unreadable.") from e
 if not isinstance(d,dict):raise SecureSettingsError("Stored m99.eu integration settings have invalid structure.")
 return d
def _normalize_back_office_template(raw:str)->str:
 value=str(raw or "").strip()
 if not value:return ""
 u=urlparse(value)
 if u.scheme!="https" or (u.hostname or "").lower()!="m99.eu":
  raise SecureSettingsError("Back Office URL must be an https://m99.eu URL.")
 path=u.path.rstrip("/")
 m=re.match(r"^(?P<admin>/[^/]+)/sell/catalog/products/(?P<id>\d+|\{id\})/edit$",path)
 if not m:
  raise SecureSettingsError("Paste a real m99.eu product EDIT URL ending in /sell/catalog/products/<id>/edit.")
 admin=m.group("admin")
 if not re.fullmatch(r"/[A-Za-z0-9_-]{6,128}",admin):
  raise SecureSettingsError("Back Office admin path is not valid.")
 return f"https://m99.eu{admin}/sell/catalog/products/{{id}}/edit"

def save_m99eu_settings(*,api_key,enabled,back_office_url="",repo_root=None,protect:Callable[[bytes],bytes]|None=None):
 protect=protect or _dpapi_protect;cur=_read_raw(repo_root);key=str(api_key or "").strip();enc=str(cur.get("api_key_dpapi_b64") or "");bo_enc=str(cur.get("back_office_url_dpapi_b64") or "")
 if key:
  if not KEY_RE.fullmatch(key):raise SecureSettingsError("PrestaShop API key must be exactly 32 letters/digits.")
  enc=base64.b64encode(protect(key.encode())).decode("ascii")
 bo_raw=str(back_office_url or "").strip()
 if bo_raw:
  bo_template=_normalize_back_office_template(bo_raw)
  bo_enc=base64.b64encode(protect(bo_template.encode())).decode("ascii")
 if not enc:raise SecureSettingsError("Enter the API key once before enabling m99.eu publishing.")
 rec={"schema":SCHEMA,"integration_id":INTEGRATION_ID,"enabled":bool(enabled),"api_key_dpapi_b64":enc,"back_office_url_dpapi_b64":bo_enc,"secret_storage":"WINDOWS_DPAPI_CURRENT_USER"}
 _atomic_write(settings_path(repo_root),json.dumps(rec,ensure_ascii=False,indent=2,sort_keys=True));return public_m99eu_status(repo_root=repo_root)
def load_m99eu_secret(*,repo_root=None,unprotect:Callable[[bytes],bytes]|None=None):
 unprotect=unprotect or _dpapi_unprotect;d=_read_raw(repo_root);enc=str(d.get("api_key_dpapi_b64") or "")
 if not enc:return ""
 try:key=unprotect(base64.b64decode(enc.encode("ascii"),validate=True)).decode().strip()
 except Exception as e:raise SecureSettingsError("Stored m99.eu API key could not be decrypted for this Windows user.") from e
 if not KEY_RE.fullmatch(key):raise SecureSettingsError("Stored m99.eu API key has invalid format.")
 return key
def load_back_office_template(*,repo_root=None,unprotect:Callable[[bytes],bytes]|None=None):
 unprotect=unprotect or _dpapi_unprotect;d=_read_raw(repo_root);enc=str(d.get("back_office_url_dpapi_b64") or "")
 if not enc:return ""
 try:value=unprotect(base64.b64decode(enc.encode("ascii"),validate=True)).decode().strip()
 except Exception as e:raise SecureSettingsError("Stored m99.eu Back Office URL could not be decrypted for this Windows user.") from e
 return _normalize_back_office_template(value)

def back_office_product_url(product_id,*,repo_root=None,unprotect:Callable[[bytes],bytes]|None=None):
 pid=str(product_id or "").strip()
 if not pid.isdigit() or int(pid)<=0:return ""
 template=load_back_office_template(repo_root=repo_root,unprotect=unprotect)
 return template.replace("{id}",str(int(pid))) if template else ""

def public_m99eu_status(*,repo_root=None):
 d=_read_raw(repo_root);return {"configured":bool(d.get("api_key_dpapi_b64")),"enabled":bool(d.get("enabled",False)),"back_office_configured":bool(d.get("back_office_url_dpapi_b64")),"secret_storage":str(d.get("secret_storage") or "NOT_CONFIGURED"),"masked_api_key":"••••••••••••••••••••••••••••••••" if d.get("api_key_dpapi_b64") else "","restart_required":False}
def effective_m99eu_credentials(*,repo_root=None):
 st=public_m99eu_status(repo_root=repo_root)
 if st["configured"]:return bool(st["enabled"]),load_m99eu_secret(repo_root=repo_root),"M99_SECURE_SETTINGS"
 return os.getenv("M99EU_CANONICAL_PILOT_ENABLED","").strip()=="1",os.getenv("M99EU_API_KEY","").strip(),"LEGACY_ENV_FALLBACK"
def verify_m99eu_connection(api_key:str):
 if not KEY_RE.fullmatch(str(api_key or "").strip()):raise SecureSettingsError("Stored API key is missing or invalid.")
 from app.services.v073_phase45.m99eu_operator_single_publish import _curl
 status,content=_curl(api_key,"/api/products?schema=blank")
 if status!="200":raise SecureSettingsError(f"m99.eu API test failed HTTP {status}: "+re.sub(r"\s+"," ",str(content or ""))[:240])
 if "<product" not in str(content or ""):raise SecureSettingsError("m99.eu API test returned HTTP 200 but no product schema.")
 return {"ok":True,"http_status":"200","scope":"products:read/schema"}
