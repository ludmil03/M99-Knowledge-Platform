from __future__ import annotations
from dataclasses import dataclass
class WriteLocked(RuntimeError):pass
class AmbiguousWrite(RuntimeError):pass
@dataclass(frozen=True)
class WriteRequest:
 operation:str;path:str;xml:str;scope_token:str
@dataclass(frozen=True)
class WriteResult:
 status:str;product_id:str|None;readback_ok:bool;retry_performed:bool=False;write_performed:bool=False
class LockedPS9WriteTransport:
 """Production-shaped boundary. Deliberately hard locked in this milestone."""
 def __init__(self,*,unlock=False):
  if unlock:raise WriteLocked("LIVE_WRITE_NOT_AUTHORIZED_IN_STAGE5_MAXSIM")
  self.calls=[]
 def execute(self,request:WriteRequest):
  raise WriteLocked("LIVE_WRITE_NOT_AUTHORIZED_IN_STAGE5_MAXSIM")
class SimulatedOneShotPS9:
 """No network. Models exactly one POST/PUT followed by mandatory GET readback."""
 def __init__(self,outcome="success",readback_ok=True):
  self.outcome=outcome;self.readback_ok=readback_ok;self.calls=[]
 def execute(self,request):
  if request.operation not in {"CREATE","UPDATE"}:raise ValueError("OPERATION_BLOCKED")
  method="POST" if request.operation=="CREATE" else "PUT"
  self.calls.append((method,request.path))
  if self.outcome in {"timeout","disconnect","ambiguous"}:raise AmbiguousWrite("AMBIGUOUS_WRITE_STOP_NO_RETRY")
  if self.outcome!="success":raise RuntimeError("WRITE_FAILED")
  self.calls.append(("GET",request.path))
  return WriteResult("READBACK_OK" if self.readback_ok else "READBACK_FAILED","123",self.readback_ok,False,True)
def execute_authorized_simulation(*,plan,submitted_token,submitted_operation,submitted_reference,submitted_target,transport):
 from app.services.stage5_production_authorization import validate_submission
 validate_submission(plan,submitted_token=submitted_token,submitted_operation=submitted_operation,submitted_reference=submitted_reference,submitted_target=submitted_target)
 req=WriteRequest(plan.operation,"/api/products" if plan.operation=="CREATE" else "/api/products/by-reference/"+plan.reference,plan.payload_xml,plan.scope_token)
 try:return transport.execute(req)
 except AmbiguousWrite:raise
