from __future__ import annotations
import hashlib, json, os, tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "m99.phase46.r4.durable_enrichment.v2"

def _root() -> Path:
    override=os.getenv("M99_PHASE46_DRAFT_STORE","").strip()
    if override:return Path(override).expanduser().resolve()
    return Path(__file__).resolve().parents[4] / "var" / "phase46_draft_enrichment"

def _canon(obj:Any)->bytes:
    return json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":"),default=str).encode("utf-8")

def save(*,job_id:int,item_id:int,supplier_reference:str,manufacturer_evidence:dict,content_bundle:dict,target:str,supplier_evidence:dict|None=None)->dict:
    if int(job_id)<=0 or int(item_id)<=0:raise ValueError("Positive job/item id required")
    ref=str(supplier_reference or "").strip()
    if not ref:raise ValueError("Supplier/manufacturer reference required")
    langs=list(content_bundle.get("languages") or [])
    docs=content_bundle.get("documents") or {}
    if target=="m99eu" and not {"EN","BG","RU"}.issubset(set(langs)):raise ValueError("m99.eu durable bundle requires EN/BG/RU")
    if any(x not in docs for x in langs):raise ValueError("Content bundle documents incomplete")
    body={"schema":SCHEMA,"job_id":int(job_id),"item_id":int(item_id),"supplier_reference":ref,"target":str(target),"supplier_evidence":supplier_evidence or {},"manufacturer_evidence":manufacturer_evidence,"content_bundle":content_bundle,"confirmed_at_utc":datetime.now(timezone.utc).isoformat()}
    body["payload_sha256"]=hashlib.sha256(_canon(body)).hexdigest()
    root=_root(); root.mkdir(parents=True,exist_ok=True)
    dest=root/f"job-{int(job_id)}.json"
    fd,tmp=tempfile.mkstemp(prefix=dest.name+'.',suffix='.tmp',dir=str(root)); os.close(fd)
    try:
        Path(tmp).write_bytes(_canon(body)+b"\n")
        os.replace(tmp,dest)
    finally:
        if os.path.exists(tmp):os.unlink(tmp)
    check=load(job_id)
    if check.get("payload_sha256")!=body["payload_sha256"]:raise RuntimeError("Durable readback checksum mismatch")
    return {"persisted":True,"reason":"PERSISTED_TO_PHASE46_DURABLE_STORE","path":str(dest),"payload_sha256":body["payload_sha256"],"languages":langs}

def load(job_id:int)->dict:
    p=_root()/f"job-{int(job_id)}.json"
    if not p.is_file():return {}
    obj=json.loads(p.read_text(encoding="utf-8"))
    sha=obj.pop("payload_sha256",""); calc=hashlib.sha256(_canon(obj)).hexdigest(); obj["payload_sha256"]=sha
    if sha!=calc:raise RuntimeError("Durable enrichment checksum mismatch")
    return obj
