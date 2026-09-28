from dataclasses import dataclass
from enum import StrEnum
from typing import Callable,Mapping,Sequence
from app.services.channel_registry_bridge import resolve_governed_target_scope
class PublishOperation(StrEnum): CREATE="CREATE"; UPDATE="UPDATE"
class WriteOutcome(StrEnum): CONFIRMED="CONFIRMED"; REJECTED="REJECTED"; AMBIGUOUS="AMBIGUOUS"
@dataclass(frozen=True)
class PublishAuthorization:
 operator_confirmed:bool; displayed_scope_token:str; submitted_scope_token:str; requested_targets:tuple[str,...]; qa_ready:bool; price_vat_ready:bool; languages_ready:bool; m99_id:str|None; identity_state:str
@dataclass(frozen=True)
class ChannelWritePlan:
 target:str; operation:PublishOperation; m99_id:str|None; blockers:tuple[str,...]; authorized:bool
@dataclass(frozen=True)
class ChannelWriteResult:
 target:str; operation:PublishOperation; outcome:WriteOutcome; remote_id:str|None; readback_pass:bool; retry_allowed:bool; blocker:str|None=None
def authorize_channel_plans(a):
 b=[]
 if not a.operator_confirmed:b.append("OPERATOR_CONFIRMATION_REQUIRED")
 if not a.displayed_scope_token or a.displayed_scope_token!=a.submitted_scope_token:b.append("DISPLAYED_SCOPE_MISMATCH")
 if not a.qa_ready:b.append("QA_NOT_READY")
 if not a.price_vat_ready:b.append("PRICE_VAT_NOT_READY")
 if not a.languages_ready:b.append("CHANNEL_LANGUAGES_NOT_READY")
 s=resolve_governed_target_scope(a.requested_targets)
 state=(a.identity_state or "").upper()
 if state not in ("NEW","EXISTING"):b.append("IDENTITY_NOT_READY")
 if state=="EXISTING" and not a.m99_id:b.append("EXISTING_REQUIRES_M99_ID")
 if state=="NEW" and a.m99_id:b.append("NEW_MUST_NOT_PREALLOCATE_M99_ID")
 op=PublishOperation.UPDATE if state=="EXISTING" else PublishOperation.CREATE
 return tuple(ChannelWritePlan(t,op,a.m99_id,tuple(dict.fromkeys(b+(["TARGET_NOT_READY:"+t] if t not in s["ready_targets"] else []))),not b and t in s["ready_targets"]) for t in a.requested_targets)
def execute_authorized_plan(p,*,create=None,update=None,readback,audit):
 if not p.authorized:audit(p,"BLOCKED",None);return ChannelWriteResult(p.target,p.operation,WriteOutcome.REJECTED,None,False,False,"BLOCKED")
 w=create if p.operation==PublishOperation.CREATE else update
 if w is None:audit(p,"BLOCKED_NO_ADAPTER",None);return ChannelWriteResult(p.target,p.operation,WriteOutcome.REJECTED,None,False,False,"WRITE_ADAPTER_NOT_PROVEN")
 try:r=w(p)
 except Exception:audit(p,"AMBIGUOUS_WRITE",None);return ChannelWriteResult(p.target,p.operation,WriteOutcome.AMBIGUOUS,None,False,False,"NO_AUTO_RETRY")
 if not isinstance(r,Mapping) or not r.get("confirmed"):audit(p,"AMBIGUOUS_WRITE",r if isinstance(r,Mapping) else None);return ChannelWriteResult(p.target,p.operation,WriteOutcome.AMBIGUOUS,None,False,False,"NO_AUTO_RETRY")
 try:rb=bool(readback(p,r))
 except Exception:rb=False
 audit(p,"CONFIRMED_READBACK" if rb else "READBACK_FAILED",r)
 return ChannelWriteResult(p.target,p.operation,WriteOutcome.CONFIRMED,str(r.get("remote_id") or "") or None,rb,False,None if rb else "MANDATORY_READBACK_FAILED")
