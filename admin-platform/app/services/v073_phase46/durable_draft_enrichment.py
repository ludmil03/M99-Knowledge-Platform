from __future__ import annotations
import hashlib, json, os, tempfile, re
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


def find_confirmed_exact(*,supplier_reference:str,target:str,product_url:str="")->dict:
    """Find the newest checksum-verified confirmed enrichment for the exact supplier product.

    Cross-job reuse is deliberately narrow: exact supplier reference + exact target and,
    when both sides provide it, exact supplier product URL. It never performs fuzzy matching,
    brand-wide inference, or Supplier == Manufacturer inference.
    """
    ref=str(supplier_reference or "").strip()
    tgt=str(target or "").strip()
    url=str(product_url or "").strip().rstrip("/")
    if not ref or not tgt:
        return {}

    candidates=[]
    for p in _root().glob("job-*.json"):
        m=re.fullmatch(r"job-(\d+)\.json",p.name)
        if not m:
            continue
        try:
            obj=load(int(m.group(1)))
        except Exception:
            # A corrupt sidecar must never become reusable evidence.
            continue

        if str(obj.get("supplier_reference") or "").strip()!=ref:
            continue
        if str(obj.get("target") or "").strip()!=tgt:
            continue

        stored_supplier=dict(obj.get("supplier_evidence") or {})
        stored_url=str(stored_supplier.get("url") or "").strip().rstrip("/")
        if url and stored_url and url!=stored_url:
            continue

        manufacturer=dict(obj.get("manufacturer_evidence") or {})
        content=dict(obj.get("content_bundle") or {})
        if manufacturer.get("status") not in {"OPERATOR_CONFIRMED_EXACT","CONFIRMED_EXACT"}:
            continue
        if not content.get("documents"):
            continue

        candidates.append(obj)

    if not candidates:
        return {}

    # ISO-8601 UTC strings sort chronologically. Fall back to job id for legacy records.
    candidates.sort(
        key=lambda x:(str(x.get("confirmed_at_utc") or ""),int(x.get("job_id") or 0)),
        reverse=True,
    )
    return candidates[0]
