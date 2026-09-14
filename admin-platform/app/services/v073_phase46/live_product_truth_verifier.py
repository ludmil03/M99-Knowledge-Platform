
from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Callable
from urllib.parse import urlencode
import xml.etree.ElementTree as ET

class ProductTruthError(RuntimeError):
    pass

@dataclass(frozen=True)
class ProductTruthResult:
    verified: bool
    product_id: str
    reference: str
    direct_http: str
    id_filter_http: str
    reference_filter_http: str
    active: str
    available_for_order: str
    visibility: str
    category_id: str
    price: str
    id_shop_default: str
    associations_summary: tuple[str, ...]
    structural_warnings: tuple[str, ...]
    blockers: tuple[str, ...]
    evidence: tuple[str, ...]

def _money(raw: Any) -> str:
    try:
        return f"{Decimal(str(raw or '').strip().replace(',', '.')):.2f}"
    except (InvalidOperation, ValueError):
        return ""

def _tag_text(node: ET.Element | None, tag: str) -> str:
    if node is None:
        return ""
    n = node.find(tag)
    if n is None:
        n = node.find(f".//{tag}")
    return (n.text or "").strip() if n is not None else ""

def _parse_product_nodes(xml_text: str) -> list[dict[str, str]]:
    try:
        root = ET.fromstring(str(xml_text or ""))
    except ET.ParseError as exc:
        raise ProductTruthError("PrestaShop returned invalid XML during truth verification.") from exc
    rows = []
    for p in root.findall(".//product"):
        rows.append({
            "id": _tag_text(p, "id"),
            "reference": _tag_text(p, "reference"),
            "active": _tag_text(p, "active"),
            "available_for_order": _tag_text(p, "available_for_order"),
            "visibility": _tag_text(p, "visibility"),
            "id_category_default": _tag_text(p, "id_category_default"),
            "price": _tag_text(p, "price"),
            "id_shop_default": _tag_text(p, "id_shop_default"),
            "mpn": _tag_text(p, "mpn"),
        })
    return rows

def _all_texts(root: ET.Element, xpath: str) -> tuple[str, ...]:
    vals=[]
    for n in root.findall(xpath):
        t=(n.text or "").strip()
        if t and t not in vals:
            vals.append(t)
    return tuple(vals)

def _parse_product_structure(xml_text: str) -> dict[str, Any]:
    try:
        root=ET.fromstring(str(xml_text or ""))
    except ET.ParseError as exc:
        raise ProductTruthError("PrestaShop returned invalid XML during structural diagnostics.") from exc
    p=root.find(".//product")
    if p is None:
        return {"id":"","reference":"","id_shop_default":"","id_category_default":"","categories":(),"images":(),"combinations":(),"stock_availables":(),"name_language_ids":(),"link_rewrite_language_ids":()}
    def lang_ids(tag:str)->tuple[str,...]:
        parent=p.find(tag)
        if parent is None:return ()
        vals=[]
        for n in parent.findall(".//language"):
            lid=str(n.attrib.get("id") or "").strip()
            if lid and lid not in vals:vals.append(lid)
        return tuple(vals)
    return {
        "id":_tag_text(p,"id"),
        "reference":_tag_text(p,"reference"),
        "id_shop_default":_tag_text(p,"id_shop_default"),
        "id_category_default":_tag_text(p,"id_category_default"),
        "categories":_all_texts(p,"./associations/categories/category/id"),
        "images":_all_texts(p,"./associations/images/image/id"),
        "combinations":_all_texts(p,"./associations/combinations/combination/id"),
        "stock_availables":_all_texts(p,"./associations/stock_availables/stock_available/id"),
        "name_language_ids":lang_ids("name"),
        "link_rewrite_language_ids":lang_ids("link_rewrite"),
    }

def compare_product_structure(target:dict[str,Any], known_good:dict[str,Any]) -> tuple[tuple[str,...],tuple[str,...]]:
    summary=[];warnings=[]
    summary.extend((
        f"TARGET_SHOP_DEFAULT={target.get('id_shop_default') or '—'}",
        f"KNOWN_GOOD_SHOP_DEFAULT={known_good.get('id_shop_default') or '—'}",
        f"TARGET_CATEGORIES={len(target.get('categories') or ())}",
        f"KNOWN_GOOD_CATEGORIES={len(known_good.get('categories') or ())}",
        f"TARGET_NAME_LANGS={','.join(target.get('name_language_ids') or ()) or '—'}",
        f"KNOWN_GOOD_NAME_LANGS={','.join(known_good.get('name_language_ids') or ()) or '—'}",
        f"TARGET_LINK_REWRITE_LANGS={','.join(target.get('link_rewrite_language_ids') or ()) or '—'}",
        f"KNOWN_GOOD_LINK_REWRITE_LANGS={','.join(known_good.get('link_rewrite_language_ids') or ()) or '—'}",
        f"TARGET_STOCK_ASSOC={len(target.get('stock_availables') or ())}",
        f"KNOWN_GOOD_STOCK_ASSOC={len(known_good.get('stock_availables') or ())}",
    ))
    if target.get("id_shop_default") and known_good.get("id_shop_default") and target.get("id_shop_default")!=known_good.get("id_shop_default"):
        warnings.append("SHOP_DEFAULT_MISMATCH")
    if not target.get("categories"):warnings.append("TARGET_HAS_NO_CATEGORY_ASSOCIATIONS")
    if not target.get("name_language_ids"):warnings.append("TARGET_HAS_NO_NAME_LANGUAGES")
    if not target.get("link_rewrite_language_ids"):warnings.append("TARGET_HAS_NO_LINK_REWRITE_LANGUAGES")
    if not target.get("stock_availables"):warnings.append("TARGET_HAS_NO_STOCK_ASSOCIATION")
    if known_good.get("name_language_ids") and target.get("name_language_ids") and set(target["name_language_ids"])!=set(known_good["name_language_ids"]):
        warnings.append("LANGUAGE_SET_DIFFERS_FROM_KNOWN_GOOD")
    return tuple(summary),tuple(warnings)

def compare_with_known_good(api_key:str,*,target_product_id:str|int,target_reference:str,known_good_product_id:str|int,curl_fn:Callable[...,tuple[str,str]]|None=None)->tuple[tuple[str,...],tuple[str,...]]:
    if curl_fn is None:
        from app.services.v073_phase45.m99eu_operator_single_publish import _curl as curl_fn
    tid=str(target_product_id or "").strip();gid=str(known_good_product_id or "").strip()
    if not tid.isdigit() or int(tid)<=0 or not gid.isdigit() or int(gid)<=0:
        raise ProductTruthError("Target and known-good product IDs must be positive integers.")
    st,ct,et=_safe_get(curl_fn,api_key,f"/api/products/{int(tid)}")
    sg,cg,eg=_safe_get(curl_fn,api_key,f"/api/products/{int(gid)}")
    if st!="200":return (), (f"TARGET_STRUCTURAL_GET_FAILED:{st}:{et}",)
    if sg!="200":return (), (f"KNOWN_GOOD_STRUCTURAL_GET_FAILED:{sg}:{eg}",)
    target=_parse_product_structure(ct);known=_parse_product_structure(cg)
    if target.get("reference")!=str(target_reference or "").strip():
        return (), ("TARGET_REFERENCE_MISMATCH_DURING_STRUCTURAL_CHECK",)
    return compare_product_structure(target,known)

def _exact_one(rows: list[dict[str, str]], *, product_id: str, reference: str) -> dict[str, str] | None:
    hits = [r for r in rows if str(r.get("id") or "") == str(product_id) and str(r.get("reference") or "") == str(reference)]
    return hits[0] if len(hits) == 1 else None


def _filter_path(field: str, value: str) -> str:
    query = urlencode({f"filter[{field}]": f"[{value}]", "display": "full"})
    path = f"/api/products?{query}"
    if "[" in path or "]" in path:
        raise ProductTruthError("Internal error: raw square brackets leaked into curl URL.")
    return path

def _safe_get(curl_fn, api_key: str, path: str) -> tuple[str, str, str]:
    try:
        status, content = curl_fn(api_key, path)
        return str(status), str(content or ""), ""
    except Exception as exc:
        return "TRANSPORT_ERROR", "", f"{type(exc).__name__}: {exc}"

def verify_product_truth(
    api_key: str,
    *,
    product_id: str | int,
    reference: str,
    expected_category_id: str | int | None = None,
    expected_price: str | None = None,
    require_hidden: bool = True,
    known_good_product_id: str | int | None = None,
    curl_fn: Callable[..., tuple[str, str]] | None = None,
) -> ProductTruthResult:
    pid = str(product_id or "").strip()
    ref = str(reference or "").strip()
    if not pid.isdigit() or int(pid) <= 0:
        raise ProductTruthError("Product ID must be a positive integer.")
    if not ref:
        raise ProductTruthError("Canonical reference is required.")

    if curl_fn is None:
        from app.services.v073_phase45.m99eu_operator_single_publish import _curl as curl_fn

    blockers: list[str] = []
    evidence: list[str] = []

    s1, c1, e1 = _safe_get(curl_fn, api_key, f"/api/products/{int(pid)}")
    direct_rows = _parse_product_nodes(c1) if s1 == "200" else []
    direct = _exact_one(direct_rows, product_id=pid, reference=ref)
    if s1 == "TRANSPORT_ERROR":
        blockers.append(f"Direct GET transport error: {e1}")
    elif s1 != "200":
        blockers.append(f"Direct GET /api/products/{pid} returned HTTP {s1}.")
    elif direct is None:
        blockers.append("Direct GET did not return exactly one product with matching ID + canonical reference.")
    else:
        evidence.append("DIRECT_GET_ID_REFERENCE_MATCH")

    id_path = _filter_path("id", str(int(pid)))
    s2, c2, e2 = _safe_get(curl_fn, api_key, id_path)
    id_rows = _parse_product_nodes(c2) if s2 == "200" else []
    by_id = _exact_one(id_rows, product_id=pid, reference=ref)
    if s2 == "TRANSPORT_ERROR":
        blockers.append(f"ID-filter GET transport error: {e2}")
    elif s2 != "200":
        blockers.append(f"ID-filter GET returned HTTP {s2}.")
    elif by_id is None:
        blockers.append("ID-filter GET did not independently return exactly one matching product.")
    else:
        evidence.append("ID_FILTER_MATCH")

    ref_path = _filter_path("reference", ref)
    s3, c3, e3 = _safe_get(curl_fn, api_key, ref_path)
    ref_rows = _parse_product_nodes(c3) if s3 == "200" else []
    by_ref = _exact_one(ref_rows, product_id=pid, reference=ref)
    if s3 == "TRANSPORT_ERROR":
        blockers.append(f"Reference-filter GET transport error: {e3}")
    elif s3 != "200":
        blockers.append(f"Reference-filter GET returned HTTP {s3}.")
    elif by_ref is None:
        blockers.append("Reference-filter GET did not independently return exactly one matching product.")
    else:
        evidence.append("REFERENCE_FILTER_MATCH")

    state = direct or by_id or by_ref or {}
    if require_hidden and state:
        expected_hidden = {
            "active": "0",
            "available_for_order": "0",
            "visibility": "none",
        }
        for key, expected in expected_hidden.items():
            got = str(state.get(key) or "")
            if got != expected:
                blockers.append(f"Hidden-state mismatch {key}: expected {expected!r}, got {got!r}.")
        if not any(x.startswith("Hidden-state mismatch") for x in blockers):
            evidence.append("SAFE_HIDDEN_STATE_MATCH")

    if expected_category_id is not None and state:
        exp = str(int(expected_category_id))
        got = str(state.get("id_category_default") or "")
        if got != exp:
            blockers.append(f"Category mismatch: expected {exp}, got {got!r}.")
        else:
            evidence.append("CATEGORY_MATCH")

    if expected_price is not None and state:
        exp = _money(expected_price)
        got = _money(state.get("price"))
        if not exp or got != exp:
            blockers.append(f"Price mismatch: expected {exp!r}, got {got!r}.")
        else:
            evidence.append("PRICE_MATCH")

    associations_summary=()
    structural_warnings=()
    if known_good_product_id is not None:
        associations_summary,structural_warnings=compare_with_known_good(
            api_key,target_product_id=pid,target_reference=ref,known_good_product_id=known_good_product_id,curl_fn=curl_fn
        )

    verified = not blockers and direct is not None and by_id is not None and by_ref is not None
    return ProductTruthResult(
        verified=verified,
        product_id=pid,
        reference=ref,
        direct_http=str(s1),
        id_filter_http=str(s2),
        reference_filter_http=str(s3),
        active=str(state.get("active") or ""),
        available_for_order=str(state.get("available_for_order") or ""),
        visibility=str(state.get("visibility") or ""),
        category_id=str(state.get("id_category_default") or ""),
        price=_money(state.get("price")),
        id_shop_default=str(state.get("id_shop_default") or ""),
        associations_summary=tuple(associations_summary),
        structural_warnings=tuple(structural_warnings),
        blockers=tuple(blockers),
        evidence=tuple(evidence),
    )
