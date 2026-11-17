from __future__ import annotations
from dataclasses import dataclass
from hashlib import sha256
from decimal import Decimal, InvalidOperation
import xml.etree.ElementTree as ET
import json,re
RID=re.compile(r"^M99 [0-9]{6}$")
@dataclass(frozen=True)
class AuthorizationPlan:
 operation:str;reference:str;target:str;scope_token:str;payload_xml:str
 publish_enabled:bool=False;write_allowed:bool=False;write_performed:bool=False
 payload_sha256:str=""
 facts_sha256:str=""
def canonical_scope(*,operation,reference,target,gross_price,vat_rate,language_map,content,variants):
 obj={"operation":operation,"reference":reference,"target":target,"gross_price":str(gross_price),"vat_rate":str(vat_rate),"language_map":dict(sorted(language_map.items())),"content":content,"variants":variants}
 return sha256(json.dumps(obj,ensure_ascii=False,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
def _bound_scope(operation,reference,target,facts_hash,payload_hash):
 obj={"operation":operation,"reference":reference,"target":target,"facts_sha256":facts_hash,"payload_sha256":payload_hash}
 return sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest()
def build_authorization(*,identity_state,reference,target,gross_price,vat_rate,language_map,content,variants,payload_xml,ready_targets):
 if target not in ready_targets:raise ValueError("TARGET_NOT_READY")
 if not RID.fullmatch(reference):raise ValueError("CANONICAL_M99_ID_REQUIRED")
 if identity_state=="EXISTING":op="UPDATE"
 elif identity_state=="NEW":op="CREATE"
 else:raise ValueError("IDENTITY_BLOCKED")
 facts_token=canonical_scope(operation=op,reference=reference,target=target,gross_price=gross_price,vat_rate=vat_rate,language_map=language_map,content=content,variants=variants)
 payload_hash=sha256(payload_xml.encode("utf-8")).hexdigest()
 token=_bound_scope(op,reference,target,facts_token,payload_hash)
 return AuthorizationPlan(op,reference,target,token,payload_xml,False,False,False,payload_hash,facts_token)
def validate_submission(plan,*,submitted_token,submitted_operation,submitted_reference,submitted_target):
 if not plan.payload_sha256 or sha256(plan.payload_xml.encode("utf-8")).hexdigest()!=plan.payload_sha256:
  raise ValueError("REVIEWED_PAYLOAD_CHANGED_REVIEW_REQUIRED")
 if not plan.facts_sha256 or _bound_scope(plan.operation,plan.reference,plan.target,plan.facts_sha256,plan.payload_sha256)!=plan.scope_token:
  raise ValueError("REVIEWED_SCOPE_CHANGED_REVIEW_REQUIRED")
 if submitted_token!=plan.scope_token:raise ValueError("SCOPE_TOKEN_MISMATCH")
 if submitted_operation!=plan.operation:raise ValueError("OPERATION_TAMPER")
 if submitted_reference!=plan.reference:raise ValueError("REFERENCE_TAMPER")
 if submitted_target!=plan.target:raise ValueError("TARGET_TAMPER")
 return True
def audit_simulation(plan,readback_ok):
 return {"operation":plan.operation,"reference":plan.reference,"target":plan.target,"scope_token":plan.scope_token,"readback_ok":bool(readback_ok),"write_performed":False,"retry_performed":False}


def validate_product_payload(plan, *, remote_id=None):
    """Validate the actual XML before a real transport can make any request.

    This is a transport boundary check, not product/business acceptance.
    Simulation plans may remain minimal; a real write requires complete XML.
    """
    if plan.target != "m99.eu" or plan.operation not in {"CREATE", "UPDATE"}:
        raise ValueError("LIVE_PLAN_TARGET_OR_OPERATION_INVALID")
    if not RID.fullmatch(plan.reference):
        raise ValueError("CANONICAL_M99_ID_REQUIRED")
    try:
        root = ET.fromstring(plan.payload_xml)
    except ET.ParseError as exc:
        raise ValueError("LIVE_PAYLOAD_XML_INVALID") from exc
    products = root.findall(".//product")
    if root.tag != "prestashop" or len(products) != 1:
        raise ValueError("LIVE_PAYLOAD_ONE_PRODUCT_REQUIRED")
    product = products[0]

    def field(name):
        nodes = product.findall(name)
        if len(nodes) != 1:
            raise ValueError("LIVE_PAYLOAD_FIELD_REQUIRED:" + name)
        return (nodes[0].text or "").strip()

    if field("reference") != plan.reference:
        raise ValueError("LIVE_PAYLOAD_REFERENCE_MISMATCH")
    ids = product.findall("id")
    if len(ids) > 1:
        raise ValueError("LIVE_PAYLOAD_PRODUCT_ID_INVALID")
    payload_id = (ids[0].text or "").strip() if ids else ""
    if plan.operation == "CREATE" and payload_id:
        raise ValueError("CREATE_PAYLOAD_MUST_NOT_HAVE_ID")
    if plan.operation == "UPDATE":
        if not payload_id.isascii() or not payload_id.isdigit() or int(payload_id) <= 0:
            raise ValueError("UPDATE_PAYLOAD_ID_REQUIRED")
        if remote_id is not None and payload_id != str(remote_id):
            raise ValueError("UPDATE_PAYLOAD_REMOTE_ID_MISMATCH")
    for name in ("id_category_default", "id_tax_rules_group"):
        value = field(name)
        if not value.isascii() or not value.isdigit() or int(value) <= 0:
            raise ValueError("LIVE_PAYLOAD_POSITIVE_ID_REQUIRED:" + name)
    try:
        price = Decimal(field("price"))
    except InvalidOperation as exc:
        raise ValueError("LIVE_PAYLOAD_PRICE_INVALID") from exc
    if not price.is_finite() or price <= 0:
        raise ValueError("LIVE_PAYLOAD_PRICE_INVALID")
    for name in ("active", "available_for_order"):
        if field(name) not in {"0", "1"}:
            raise ValueError("LIVE_PAYLOAD_SAFETY_FIELD_INVALID:" + name)
    if field("visibility") not in {"both", "catalog", "search", "none"}:
        raise ValueError("LIVE_PAYLOAD_VISIBILITY_INVALID")
    language_ids = None
    for name in ("name", "description", "description_short", "meta_title", "meta_description"):
        nodes = product.findall(name)
        if len(nodes) != 1:
            raise ValueError("LIVE_PAYLOAD_FIELD_REQUIRED:" + name)
        translations = nodes[0].findall("language")
        current_ids = set()
        for translation in translations:
            language_id = translation.get("id", "")
            if (not language_id.isascii() or not language_id.isdigit()
                    or int(language_id) <= 0 or language_id in current_ids
                    or not (translation.text or "").strip()):
                raise ValueError("LIVE_PAYLOAD_LANGUAGE_INVALID:" + name)
            current_ids.add(language_id)
        if not current_ids or language_ids is not None and current_ids != language_ids:
            raise ValueError("LIVE_PAYLOAD_LANGUAGE_SET_MISMATCH:" + name)
        language_ids = current_ids
    return True
