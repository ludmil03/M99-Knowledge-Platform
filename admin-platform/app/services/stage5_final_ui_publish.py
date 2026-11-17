from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
import base64, http.client, ssl, xml.etree.ElementTree as ET
from urllib.parse import urlencode, urlparse
from integrations.m99eu_prestashop.live_write_transport import OneShotPS9WriteTransport, WriteViolation, AmbiguousWrite
from integrations.m99eu_prestashop.readonly_preflight_r2 import OneShotBasicGetTransport
from app.services.stage5_production_authorization import validate_submission, validate_product_payload

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

_NUMERIC_PRODUCT_FIELDS = frozenset({
    "price", "wholesale_price", "unit_price", "unit_price_ratio", "ecotax",
    "additional_shipping_cost", "weight", "width", "height", "depth",
    "quantity", "minimal_quantity", "low_stock_threshold",
})


def _readback_value(node):
    """Compare API values without depending on XML order or transport links."""
    children = list(node)
    if children:
        # Association order is not a product fact. Preserve duplicates so a
        # duplicate/missing association cannot disappear during comparison.
        return ("children", tuple(sorted(
            (child.tag, str(child.get("id", "")), _readback_value(child))
            for child in children
        )))
    value = (node.text or "").strip()
    if value and (node.tag in _NUMERIC_PRODUCT_FIELDS or node.tag == "id"
                  or node.tag.startswith("id_")):
        try:
            number = Decimal(value)
            if not number.is_finite():
                raise InvalidOperation
            return ("number", number)
        except InvalidOperation as exc:
            raise ReadbackFailed("READBACK_INVALID_NUMBER:" + node.tag) from exc
    return ("text", value)


def _meaningful_payload_field(node):
    # PrestaShop's blank schema contains many empty, unused fields. Those do
    # not assert a value or authorize clearing existing channel data.
    return bool((node.text or "").strip()) or any(
        _meaningful_payload_field(child) for child in node
    )


def _readback(cfg,remote_id,reference,expected_payload=None):
    if expected_payload is None:
        raise ReadbackFailed("EXPECTED_PAYLOAD_REQUIRED")
    try:
        expected_root = ET.fromstring(expected_payload)
    except ET.ParseError as exc:
        raise ReadbackFailed("EXPECTED_PAYLOAD_INVALID_XML") from exc
    expected = (expected_root if expected_root.tag == "product"
                else expected_root.find(".//product"))
    if expected is None:
        raise ReadbackFailed("EXPECTED_PRODUCT_MISSING")
    for field in ("active", "available_for_order", "visibility"):
        if not (expected.findtext(field) or "").strip():
            raise ReadbackFailed("SAFETY_FIELD_NOT_IN_PAYLOAD:" + field)

    x=_get_once(cfg,f"/api/products/{remote_id}")
    try:
        root=ET.fromstring(x)
    except ET.ParseError as exc:
        raise ReadbackFailed("PRODUCT_READBACK_INVALID_XML") from exc
    product=root if root.tag == "product" else root.find(".//product")
    if product is None: raise ReadbackFailed("PRODUCT_READBACK_MISSING")
    if (product.findtext("id") or "").strip() != str(remote_id):
        raise ReadbackFailed("PRODUCT_ID_READBACK_MISMATCH")
    ref=(product.findtext("reference") or "").strip()
    if ref!=reference: raise ReadbackFailed("REFERENCE_READBACK_MISMATCH")

    for wanted in expected:
        field = wanted.tag
        if not _meaningful_payload_field(wanted):
            continue
        if len(expected.findall(field)) != 1:
            raise ReadbackFailed("EXPECTED_FIELD_DUPLICATED:" + field)
        if len(product.findall(field)) > 1:
            raise ReadbackFailed("READBACK_FIELD_DUPLICATED:" + field)
        actual = product.find(field)
        if actual is None:
            raise ReadbackFailed("READBACK_FIELD_MISSING:" + field)
        if field == "associations":
            # A category-only update does not assert removal of existing
            # images/combinations. Verify the complete membership of each
            # meaningful association group that the reviewed payload sets.
            for group in wanted:
                if not _meaningful_payload_field(group):
                    continue
                matches = actual.findall(group.tag)
                if (len(matches) != 1 or len(wanted.findall(group.tag)) != 1
                        or _readback_value(matches[0]) != _readback_value(group)):
                    raise ReadbackFailed("READBACK_MISMATCH:associations/" + group.tag)
            continue
        languages = wanted.findall("language")
        if languages:
            for label, nodes in (("EXPECTED", languages),
                                 ("READBACK", actual.findall("language"))):
                ids = [node.get("id", "") for node in nodes]
                if not all(ids) or len(ids) != len(set(ids)):
                    raise ReadbackFailed(label + "_LANGUAGE_IDS_INVALID:" + field)
            if any(not (node.text or "").strip() for node in languages):
                raise ReadbackFailed("EXPECTED_LOCALIZED_VALUE_MISSING:" + field)
        if _readback_value(actual) != _readback_value(wanted):
            raise ReadbackFailed("READBACK_MISMATCH:" + field)
    return True

def execute_ui_publish(*,cfg,plan,submitted_token,submitted_operation,submitted_reference,submitted_target,operator_confirmed):
    if operator_confirmed is not True: raise FinalPublishBlocked("OPERATOR_CONFIRMATION_REQUIRED")
    validate_submission(plan,submitted_token=submitted_token,submitted_operation=submitted_operation,submitted_reference=submitted_reference,submitted_target=submitted_target)
    validate_product_payload(plan)
    resolved=resolve_reference(cfg,plan.reference)
    if plan.operation=="CREATE" and resolved.state!="NEW": raise FinalPublishBlocked("CREATE_COLLISION")
    if plan.operation=="UPDATE" and resolved.state!="EXISTING": raise FinalPublishBlocked("UPDATE_TARGET_NOT_FOUND")
    if plan.operation=="UPDATE":
        validate_product_payload(plan, remote_id=resolved.remote_id)
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
