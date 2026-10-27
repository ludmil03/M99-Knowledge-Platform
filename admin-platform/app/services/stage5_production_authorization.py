from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
import json,re
RID=re.compile(r"^M99 [0-9]{6}$")
@dataclass(frozen=True)
class AuthorizationPlan:
 operation:str;reference:str;target:str;scope_token:str;payload_xml:str
 publish_enabled:bool=False;write_allowed:bool=False;write_performed:bool=False
def canonical_scope(*,operation,reference,target,gross_price,vat_rate,language_map,content,variants):
 obj={"operation":operation,"reference":reference,"target":target,"gross_price":str(gross_price),"vat_rate":str(vat_rate),"language_map":dict(sorted(language_map.items())),"content":content,"variants":variants}
 return sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
def build_authorization(*,identity_state,reference,target,gross_price,vat_rate,language_map,content,variants,payload_xml,ready_targets):
 if target not in ready_targets:raise ValueError("TARGET_NOT_READY")
 if not RID.fullmatch(reference):raise ValueError("CANONICAL_M99_ID_REQUIRED")
 if identity_state=="EXISTING":op="UPDATE"
 elif identity_state=="NEW":op="CREATE"
 else:raise ValueError("IDENTITY_BLOCKED")
 token=canonical_scope(operation=op,reference=reference,target=target,gross_price=gross_price,vat_rate=vat_rate,language_map=language_map,content=content,variants=variants)
 return AuthorizationPlan(op,reference,target,token,payload_xml,False,False,False)
def validate_submission(plan,*,submitted_token,submitted_operation,submitted_reference,submitted_target):
 if submitted_token!=plan.scope_token:raise ValueError("SCOPE_TOKEN_MISMATCH")
 if submitted_operation!=plan.operation:raise ValueError("OPERATION_TAMPER")
 if submitted_reference!=plan.reference:raise ValueError("REFERENCE_TAMPER")
 if submitted_target!=plan.target:raise ValueError("TARGET_TAMPER")
 return True
def audit_simulation(plan,readback_ok):
 return {"operation":plan.operation,"reference":plan.reference,"target":plan.target,"scope_token":plan.scope_token,"readback_ok":bool(readback_ok),"write_performed":False,"retry_performed":False}
