from __future__ import annotations
import xml.etree.ElementTree as ET
from app.services.stage5_production_authorization import validate_submission
from integrations.m99eu_prestashop.live_write_transport import OneShotPS9WriteTransport,AmbiguousWrite
class ReadbackViolation(RuntimeError):pass
def _remote_id(xml):
 root=ET.fromstring(xml);x=(root.findtext(".//product/id") or root.findtext(".//id") or "").strip()
 if not x:raise ReadbackViolation("REMOTE_ID_MISSING")
 return x
def _verify(reference,xml):
 root=ET.fromstring(xml);ref=(root.findtext(".//product/reference") or "").strip()
 if ref!=reference:raise ReadbackViolation("REFERENCE_READBACK_MISMATCH")
 return True
def publish_once(*,plan,submitted_token,submitted_operation,submitted_reference,submitted_target,cfg):
 validate_submission(plan,submitted_token=submitted_token,submitted_operation=submitted_operation,submitted_reference=submitted_reference,submitted_target=submitted_target)
 t=OneShotPS9WriteTransport(cfg.base_url,cfg.api_key,cfg.timeout_seconds)
 if plan.operation=="CREATE":
  response=t.request_once("POST","/api/products",plan.payload_xml);rid=_remote_id(response)
 elif plan.operation=="UPDATE":
  # Remote product id must be resolved/proven before UPDATE; never fallback to CREATE.
  raise ReadbackViolation("UPDATE_REMOTE_ID_RESOLUTION_REQUIRED")
 else:raise ReadbackViolation("OPERATION_BLOCKED")
 readback=t.request_once("GET",f"/api/products/{rid}")
 _verify(plan.reference,readback)
 return {"status":"PUBLISHED_AND_READBACK_OK","remote_id":rid,"reference":plan.reference,"operation":plan.operation,"calls":tuple(t.calls),"retry":False}
