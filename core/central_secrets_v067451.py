from __future__ import annotations
import os, json, requests
from dataclasses import dataclass
from typing import Dict, Any

REDACTED="***REDACTED***"

class SecretsError(RuntimeError): pass

@dataclass
class VaultConfig:
    addr: str
    token: str
    namespace: str|None = None
    mount: str = "secret"

def env_vault_config() -> VaultConfig:
    addr=os.environ.get("M99_VAULT_ADDR","").strip().rstrip("/")
    token=os.environ.get("M99_VAULT_TOKEN","").strip()
    namespace=os.environ.get("M99_VAULT_NAMESPACE","").strip() or None
    if not addr: raise SecretsError("M99_VAULT_ADDR is required")
    if not token: raise SecretsError("M99_VAULT_TOKEN is required")
    return VaultConfig(addr=addr,token=token,namespace=namespace)

def _headers(c:VaultConfig):
    h={"X-Vault-Token":c.token}
    if c.namespace: h["X-Vault-Namespace"]=c.namespace
    return h

def _kv2_url(c:VaultConfig,path:str):
    path=path.strip("/")
    return f"{c.addr}/v1/{c.mount}/data/{path}"

def read_secret(path:str,c:VaultConfig|None=None)->Dict[str,Any]:
    c=c or env_vault_config()
    r=requests.get(_kv2_url(c,path),headers=_headers(c),timeout=20)
    if r.status_code==404: raise SecretsError(f"Secret not found: {path}")
    if not r.ok: raise SecretsError(f"Vault read failed: HTTP {r.status_code}")
    j=r.json()
    return ((j.get("data") or {}).get("data") or {})

def write_secret(path:str,data:Dict[str,Any],c:VaultConfig|None=None):
    c=c or env_vault_config()
    r=requests.post(_kv2_url(c,path),headers={**_headers(c),"Content-Type":"application/json"},
                    json={"data":data},timeout=20)
    if not r.ok: raise SecretsError(f"Vault write failed: HTTP {r.status_code}")
    return True

def secret_exists(path:str,c:VaultConfig|None=None)->bool:
    try:
        read_secret(path,c); return True
    except SecretsError as e:
        if "not found" in str(e).lower(): return False
        raise

def validate_fields(secret:Dict[str,Any],required:list[str]):
    missing=[x for x in required if not str(secret.get(x,"")).strip()]
    return missing

def redacted_status(secret:Dict[str,Any],required:list[str]):
    return {k:(REDACTED if str(secret.get(k,"")).strip() else "MISSING") for k in required}

def get_channel_secret(channel:str,registry:Dict[str,Any],c:VaultConfig|None=None):
    spec=registry[channel]
    data=read_secret(spec["secret_path"],c)
    missing=validate_fields(data,spec["fields"])
    if missing: raise SecretsError(f"{channel}: missing fields in central vault: {missing}")
    return data
