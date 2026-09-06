from __future__ import annotations

import base64
import json
import re
import subprocess
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

BASE_URL = "https://m99.eu"
DEFAULT_CATEGORY_ID = 26
REFERENCE_PREFIX = "M99-"
REFERENCE_BASE = 900_000_000


class PublishSafetyError(RuntimeError):
    pass


@dataclass(frozen=True)
class Candidate:
    item_id: int
    title: str
    supplier_reference: str
    price: str
    description: str
    source_url: str
    provisional_m99_reference: str
    publishable: bool
    blockers: tuple[str, ...]


@dataclass(frozen=True)
class PublishResult:
    created: bool
    product_id: str
    reference: str
    active: str
    category_id: str
    http_status: str
    correlation_id: str


def _plain(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(k): _plain(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_plain(v) for v in value]
    return str(value)


def snapshot_from_item(item: Any) -> dict[str, Any]:
    data: dict[str, Any] = {}
    try:
        for k, v in vars(item).items():
            if not k.startswith("_"):
                data[k] = _plain(v)
    except Exception:
        pass

    for key in list(data):
        val = data[key]
        if isinstance(val, str) and key.lower() in {
            "snapshot", "source_snapshot", "source_snapshot_json", "payload",
            "payload_json", "data", "raw_data", "hydrated_payload", "evidence_json"
        }:
            try:
                parsed = json.loads(val)
                if isinstance(parsed, dict):
                    data[f"__expanded_{key}"] = parsed
            except Exception:
                pass
        elif isinstance(val, dict):
            data[f"__expanded_{key}"] = val
    return data


def _walk(obj: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(obj, dict):
        for k, v in obj.items():
            yield str(k), v
            yield from _walk(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from _walk(v)


def _first(data: dict[str, Any], keys: Iterable[str]) -> str:
    wanted = {k.lower() for k in keys}
    for k, v in _walk(data):
        if k.lower() in wanted and v not in (None, "", [], {}):
            if isinstance(v, (str, int, float, Decimal)):
                return str(v).strip()
    return ""


def _price(data: dict[str, Any]) -> str:
    raw = _first(data, ("price", "supplier_price", "sell_price", "selling_price",
                        "price_tax_excl", "unit_price", "amount"))
    if not raw:
        return ""
    normalized = raw.replace("\xa0", " ").replace("BGN", "").replace("EUR", "").replace("€", "")
    normalized = re.sub(r"[^0-9,.\-]", "", normalized)
    if normalized.count(",") == 1 and normalized.count(".") == 0:
        normalized = normalized.replace(",", ".")
    try:
        value = Decimal(normalized)
    except (InvalidOperation, ValueError):
        return ""
    return f"{value:.2f}" if value > 0 else ""


def provisional_reference(item_id: int) -> str:
    return f"{REFERENCE_PREFIX}{REFERENCE_BASE + int(item_id)}"


def candidate_from_item(item: Any) -> Candidate:
    item_id = int(getattr(item, "id"))
    data = snapshot_from_item(item)
    title = _first(data, ("title", "name", "product_name", "supplier_title"))
    supplier_ref = _first(data, ("supplier_reference", "supplier_ref", "reference", "sku", "mpn", "code"))
    description = _first(data, ("description", "description_short", "short_description", "details", "content"))
    source_url = _first(data, ("source_url", "url", "product_url", "supplier_url", "canonical_url"))
    price = _price(data)

    blockers: list[str] = []
    if not title:
        blockers.append("Missing hydrated product title")
    if not supplier_ref:
        blockers.append("Missing supplier reference / SKU")
    if not price:
        blockers.append("Missing or invalid positive price")

    return Candidate(
        item_id=item_id,
        title=title or f"Import item #{item_id}",
        supplier_reference=supplier_ref,
        price=price,
        description=description,
        source_url=source_url,
        provisional_m99_reference=provisional_reference(item_id),
        publishable=not blockers,
        blockers=tuple(blockers),
    )


def _curl(api_key: str, path: str, method: str = "GET", body: str | None = None) -> tuple[str, str]:
    key = api_key.strip()
    if not re.fullmatch(r"[A-Za-z0-9]{32}", key):
        raise PublishSafetyError("PrestaShop API key must be exactly 32 alphanumeric characters.")

    auth = base64.b64encode((key + ":").encode("ascii")).decode("ascii")
    url = BASE_URL.rstrip("/") + path
    temp_dir = Path.cwd()
    out_file = temp_dir / f".m99_api_{uuid.uuid4().hex}.tmp"
    body_file: Path | None = None
    try:
        args = [
            "curl.exe", "--silent", "--show-error", "--location",
            "--ipv4", "--http1.1", "--connect-timeout", "15", "--max-time", "45",
            "-H", "Accept: application/xml",
            "-H", "Connection: close",
            "-H", "User-Agent: M99-Knowledge-Platform/Rev31-Phase4.2",
            "-H", f"Authorization: Basic {auth}",
            "-o", str(out_file), "-w", "%{http_code}", "-X", method,
        ]
        if body is not None:
            body_file = temp_dir / f".m99_body_{uuid.uuid4().hex}.xml"
            body_file.write_text(body, encoding="utf-8")
            args += ["-H", "Content-Type: application/xml", "-H", "Expect:", "--data-binary", f"@{body_file}"]
        args.append(url)

        cp = subprocess.run(args, capture_output=True, text=True, timeout=60)
        content = out_file.read_text(encoding="utf-8", errors="replace") if out_file.exists() else ""
        if cp.returncode != 0:
            raise PublishSafetyError(f"curl transport failed with exit code {cp.returncode}: {cp.stderr.strip()}")
        return cp.stdout.strip(), content
    finally:
        out_file.unlink(missing_ok=True)
        if body_file:
            body_file.unlink(missing_ok=True)


def _xml_text(node: ET.Element | None, tag: str) -> str:
    if node is None:
        return ""
    found = node.find(f".//{tag}")
    return (found.text or "").strip() if found is not None else ""


def active_languages(api_key: str) -> list[tuple[str, str]]:
    status, content = _curl(api_key, "/api/languages?display=full")
    if status != "200":
        raise PublishSafetyError(f"Languages read failed with HTTP {status}.")
    root = ET.fromstring(content)
    langs: list[tuple[str, str]] = []
    for node in root.findall(".//language"):
        lid = _xml_text(node, "id")
        iso = _xml_text(node, "iso_code").lower()
        active = _xml_text(node, "active")
        if lid and iso and active in ("", "1"):
            langs.append((lid, iso))
    if not langs:
        raise PublishSafetyError("No active PrestaShop languages could be parsed.")
    return langs


def ensure_category(api_key: str, category_id: int) -> None:
    status, _ = _curl(api_key, f"/api/categories/{int(category_id)}")
    if status != "200":
        raise PublishSafetyError(f"Target category {category_id} is not API-readable (HTTP {status}).")


def _find_existing(api_key: str, reference: str) -> str:
    from urllib.parse import quote
    filt = quote(f"[{reference}]", safe="")
    status, content = _curl(api_key, f"/api/products?filter%5Breference%5D={filt}&display=%5Bid,reference,active,id_category_default%5D")
    if status != "200":
        raise PublishSafetyError(f"Duplicate check failed with HTTP {status}.")
    root = ET.fromstring(content)
    p = root.find(".//product")
    if p is None:
        return ""
    pid = p.attrib.get("id", "") or _xml_text(p, "id")
    return pid.strip()


def _lang_xml(field: str, langs: list[tuple[str, str]], values: dict[str, str], default: str) -> str:
    parts = [f"<{field}>"]
    for lid, iso in langs:
        val = values.get(iso, default)
        safe = val.replace("]]>", "]]]]><![CDATA[>")
        parts.append(f'<language id="{escape(lid)}"><![CDATA[{safe}]]></language>')
    parts.append(f"</{field}>")
    return "".join(parts)


def _slug(text: str, fallback: str) -> str:
    s = text.lower()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    s = s.strip("-")
    return (s[:120] or fallback.lower())


def build_payload(candidate: Candidate, category_id: int, langs: list[tuple[str, str]]) -> str:
    if not candidate.publishable:
        raise PublishSafetyError("Selected M99 item is not publishable: " + "; ".join(candidate.blockers))
    name = candidate.title[:127]
    desc = candidate.description or f"Imported from verified M99 supplier evidence. Supplier reference: {candidate.supplier_reference}."
    slug = _slug(candidate.title, candidate.provisional_m99_reference)
    names = {iso: name for _, iso in langs}
    descs = {iso: desc for _, iso in langs}
    slugs = {iso: slug for _, iso in langs}

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<prestashop xmlns:xlink="http://www.w3.org/1999/xlink"><product>'
        '<active><![CDATA[0]]></active>'
        '<available_for_order><![CDATA[0]]></available_for_order>'
        '<show_price><![CDATA[1]]></show_price>'
        f'<price><![CDATA[{candidate.price}]]></price>'
        f'<reference><![CDATA[{candidate.provisional_m99_reference}]]></reference>'
        f'<supplier_reference><![CDATA[{candidate.supplier_reference}]]></supplier_reference>'
        f'<id_category_default><![CDATA[{int(category_id)}]]></id_category_default>'
        + _lang_xml("name", langs, names, name)
        + _lang_xml("description_short", langs, descs, desc)
        + _lang_xml("description", langs, descs, desc)
        + _lang_xml("meta_title", langs, names, name)
        + _lang_xml("link_rewrite", langs, slugs, slug)
        + f'<associations><categories><category><id><![CDATA[{int(category_id)}]]></id></category></categories></associations>'
        '</product></prestashop>'
    )


def readback(api_key: str, product_id: str) -> tuple[str, str, str]:
    status, content = _curl(api_key, f"/api/products/{product_id}")
    if status != "200":
        raise PublishSafetyError(f"Read-back failed with HTTP {status}.")
    root = ET.fromstring(content)
    p = root.find(".//product")
    if p is None:
        raise PublishSafetyError("Read-back XML has no product node.")
    return _xml_text(p, "reference"), _xml_text(p, "active"), _xml_text(p, "id_category_default")


def publish_one(candidate: Candidate, api_key: str, category_id: int, confirmation: str) -> PublishResult:
    if confirmation.strip() != "CREATE ONE PRODUCT":
        raise PublishSafetyError("Exact confirmation phrase is required.")
    if not candidate.publishable:
        raise PublishSafetyError("Selected M99 item is blocked: " + "; ".join(candidate.blockers))

    correlation_id = uuid.uuid4().hex
    langs = active_languages(api_key)
    ensure_category(api_key, category_id)

    existing = _find_existing(api_key, candidate.provisional_m99_reference)
    if existing:
        ref, active, cat = readback(api_key, existing)
        if ref != candidate.provisional_m99_reference:
            raise PublishSafetyError("Duplicate guard found inconsistent product reference.")
        return PublishResult(False, existing, ref, active, cat, "EXISTING", correlation_id)

    payload = build_payload(candidate, category_id, langs)
    status, content = _curl(api_key, "/api/products", method="POST", body=payload)
    if status not in ("200", "201"):
        snippet = re.sub(r"\s+", " ", content)[:600]
        raise PublishSafetyError(f"PrestaShop rejected create with HTTP {status}: {snippet}")

    root = ET.fromstring(content)
    p = root.find(".//product")
    product_id = _xml_text(p, "id") if p is not None else ""
    if not product_id:
        product_id = _find_existing(api_key, candidate.provisional_m99_reference)
    if not product_id:
        raise PublishSafetyError("POST succeeded but product ID could not be recovered.")

    ref, active, cat = readback(api_key, product_id)
    if ref != candidate.provisional_m99_reference or active != "0" or cat != str(category_id):
        raise PublishSafetyError(
            f"Read-back mismatch: reference={ref!r}, active={active!r}, category={cat!r}"
        )
    return PublishResult(True, product_id, ref, active, cat, status, correlation_id)


def append_audit(repo_root: Path, user_label: str, candidate: Candidate, result: PublishResult) -> Path:
    audit_dir = repo_root / "admin-platform" / "data" / "publish_audit"
    audit_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc)
    record = {
        "timestamp": ts.isoformat(),
        "severity": "INFO",
        "user": user_label,
        "module": "rev31_phase4_2_operator_single_publish",
        "operation": "CREATE_ONE_INACTIVE_PRODUCT" if result.created else "READBACK_EXISTING",
        "entity": "product",
        "supplier_reference": candidate.supplier_reference,
        "m99_reference": result.reference,
        "channel": "m99.eu",
        "result": "PASS",
        "product_id": result.product_id,
        "active": result.active,
        "category_id": result.category_id,
        "correlation_id": result.correlation_id,
        "secret_logged": False,
    }
    path = audit_dir / f"{ts.strftime('%Y%m%dT%H%M%SZ')}_{result.reference}_{result.correlation_id[:8]}.json"
    path.write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding="utf-8")
    return path
