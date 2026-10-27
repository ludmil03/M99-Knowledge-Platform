from __future__ import annotations
from dataclasses import dataclass
import base64, http.client, ssl, xml.etree.ElementTree as ET
from urllib.parse import urlencode, urlparse
from integrations.m99eu_prestashop.live_write_transport import OneShotPS9WriteTransport, WriteViolation, AmbiguousWrite
from integrations.m99eu_prestashop.readonly_preflight_r2 import OneShotBasicGetTransport
from app.services.stage5_production_authorization import validate_submission

class FinalPublishBlocked(RuntimeError): pass
class ReadbackFailed(RuntimeError): pass

@dataclass(frozen=True)
class ExistingResolution:
    state:str
    remote_id:str|None
    reference:str

def _auth(api_key):
    return "Basic "+base64.b64encode((api_key+":").encode()).decode()

def _get_once(cfg,path,params=None):
    # Reuse the Windows-proven authenticated READ-ONLY transport:
    # fresh HTTPS connection per GET, Basic Auth, explicit User-Agent,
    # Connection: close, strict host/path allow-list, and NO retry.
    t=OneShotBasicGetTransport(cfg.base_url,cfg.api_key,cfg.timeout_seconds)
    return t.get(path,params)

def resolve_reference(cfg,reference):
    if not reference.startswith("M99 ") or len(reference)!=10 or not reference[4:].isdigit():
        raise FinalPublishBlocked("REFERENCE_INVALID")
    x=_get_once(cfg,"/api/products",{"display":"[id,reference]","filter[reference]":f"[{reference}]"})
    root=ET.fromstring(x); rows=root.findall(".//product")
    ids=[]
    for row in rows:
        rid=(row.findtext("id") or row.attrib.get("id") or "").strip()
        ref=(row.findtext("reference") or "").strip()
        if ref==reference and rid: ids.append(rid)
    ids=list(dict.fromkeys(ids))
    if len(ids)>1: raise FinalPublishBlocked("IDENTITY_AMBIGUOUS")
    return ExistingResolution("EXISTING" if ids else "NEW",ids[0] if ids else None,reference)

def _readback(cfg,remote_id,reference,expected_payload=None):
    x=_get_once(cfg,f"/api/products/{remote_id}")
    root=ET.fromstring(x)
    product=root.find(".//product")
    if product is None: raise ReadbackFailed("PRODUCT_READBACK_MISSING")
    ref=(product.findtext("reference") or "").strip()
    if ref!=reference: raise ReadbackFailed("REFERENCE_READBACK_MISMATCH")
    if expected_payload is None:
        raise ReadbackFailed("EXPECTED_PAYLOAD_REQUIRED")
    expected=ET.fromstring(expected_payload).find(".//product")
    if expected is None: raise ReadbackFailed("EXPECTED_PRODUCT_MISSING")
    for field in ("id_category_default","price","id_tax_rules_group","active","available_for_order","visibility"):
        wanted=expected.findtext(field)
        if wanted is None:
            if field in ("active","available_for_order","visibility"):
                raise ReadbackFailed("SAFETY_FIELD_NOT_IN_PAYLOAD:"+field)
            continue
        actual=product.findtext(field)
        if actual is None: raise ReadbackFailed("READBACK_FIELD_MISSING:"+field)
        if field=="price":
            from decimal import Decimal, InvalidOperation
            try:
                match=Decimal(actual.strip())==Decimal(wanted.strip())
            except InvalidOperation:
                match=False
        else:
            match=actual.strip()==wanted.strip()
        if not match: raise ReadbackFailed("READBACK_MISMATCH:"+field)
    return True

def execute_ui_publish(*,cfg,plan,submitted_token,submitted_operation,submitted_reference,submitted_target,operator_confirmed):
    if operator_confirmed is not True: raise FinalPublishBlocked("OPERATOR_CONFIRMATION_REQUIRED")
    validate_submission(plan,submitted_token=submitted_token,submitted_operation=submitted_operation,submitted_reference=submitted_reference,submitted_target=submitted_target)
    resolved=resolve_reference(cfg,plan.reference)
    if plan.operation=="CREATE" and resolved.state!="NEW": raise FinalPublishBlocked("CREATE_COLLISION")
    if plan.operation=="UPDATE" and resolved.state!="EXISTING": raise FinalPublishBlocked("UPDATE_TARGET_NOT_FOUND")
    t=OneShotPS9WriteTransport(cfg.base_url,cfg.api_key,cfg.timeout_seconds)
    if plan.operation=="CREATE":
        response=t.request_once("POST","/api/products",plan.payload_xml)
        root=ET.fromstring(response); rid=(root.findtext(".//product/id") or "").strip()
        if not rid: raise ReadbackFailed("CREATE_REMOTE_ID_MISSING")
    elif plan.operation=="UPDATE":
        rid=resolved.remote_id
        # PUT is only to the identity-proven exact remote product id.
        t.request_once("PUT",f"/api/products/{rid}",plan.payload_xml)
    else: raise FinalPublishBlocked("OPERATION_BLOCKED")
    _readback(cfg,rid,plan.reference,plan.payload_xml)
    return {"status":"PUBLISHED_READBACK_OK","operation":plan.operation,"reference":plan.reference,"remote_id":rid,"retry":False}
