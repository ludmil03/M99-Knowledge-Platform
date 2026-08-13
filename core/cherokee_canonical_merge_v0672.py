from __future__ import annotations

from datetime import datetime, timezone
from html import unescape
import re
import requests

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/150 Safari/537.36"}

MANUFACTURER_URL = "https://cherokeeuniforms.com/products/womens-2-pocket-sweetheart-v-neck-scrub-top-ckww601"
STENSO_URL = "https://stenso.net/produkt/medicinski-tuniki/4443-damska-medicinska-tunika-cherokee-v-neck-navy-wwe601"

def now():
    return datetime.now(timezone.utc).isoformat()

def clean(v):
    return re.sub(r"\s+", " ", unescape(str(v or ""))).strip()

def norm(v):
    return re.sub(r"[^a-z0-9а-я]+", "", str(v or "").lower())

def strip_html(h):
    h = re.sub(r"<script\b[^>]*>.*?</script>", " ", h or "", flags=re.I | re.S)
    h = re.sub(r"<style\b[^>]*>.*?</style>", " ", h, flags=re.I | re.S)
    return clean(re.sub(r"<[^>]+>", " ", h))

def fetch(url, timeout=30):
    r = requests.get(url, headers=UA, timeout=timeout, allow_redirects=True)
    r.raise_for_status()
    return {
        "url": r.url,
        "html": r.text,
        "status": r.status_code,
        "observed_at_utc": now(),
    }

def compare_fact(field, manufacturer_value, supplier_value):
    if manufacturer_value in (None, "", [], {}) and supplier_value in (None, "", [], {}):
        return {"field": field, "status": "UNVERIFIED", "selected": None}

    if manufacturer_value not in (None, "", [], {}) and supplier_value in (None, "", [], {}):
        return {
            "field": field,
            "status": "MANUFACTURER_ONLY",
            "selected": manufacturer_value,
            "authority": "manufacturer",
        }

    if manufacturer_value in (None, "", [], {}) and supplier_value not in (None, "", [], {}):
        return {
            "field": field,
            "status": "SUPPLIER_ONLY",
            "selected": supplier_value,
            "authority": "supplier",
            "operator_review": True,
        }

    if norm(manufacturer_value) == norm(supplier_value):
        return {
            "field": field,
            "status": "VERIFIED_CONSENSUS",
            "selected": manufacturer_value,
            "authority": "manufacturer",
        }

    return {
        "field": field,
        "status": "SOURCE_CONFLICT",
        "selected": manufacturer_value,
        "authority": "manufacturer",
        "supplier_value": supplier_value,
        "operator_review": True,
    }

def parse_manufacturer():
    page = fetch(MANUFACTURER_URL)
    text = strip_html(page["html"])
    low = text.lower()

    return {
        "authority": "AUTHORITATIVE",
        "source_url": page["url"],
        "observed_at_utc": page["observed_at_utc"],
        "official_images": [],
        "commercial_observation": {},
        "facts": {
            "brand": "Cherokee",
            "collection": "WW Revolution" if "ww revolution" in low else None,
            "canonical_style": "WW601",
            "manufacturer_item": "CK-WW601--",
            "official_name": "Women's 2-Pocket Sweetheart V-Neck Scrub Top",
            "fit": "Missy relaxed fit" if "missy relaxed fit" in low else None,
            "center_back_length_inches": 26 if "center back length: 26" in low else None,
            "neckline": "Curved V-neckline" if "curved v-neckline" in low else None,
            "sleeves": "Short sleeves" if "short sleeves" in low else None,
            "pockets": (
                "2 front patch pockets with instrument loops"
                if "2 front patch pockets with instrument loops" in low else None
            ),
            "mesh_side_panels": True if "mesh side panels" in low else None,
            "shirttail_hem": True if "shirttail hemline" in low else None,
            "material": (
                "78% polyester, 20% rayon, 2% spandex"
                if "78% polyester, 20% rayon, 2% spandex" in low else None
            ),
            "fabric": "Silky stretch twill fabric" if "silky stretch twill fabric" in low else None,
        },
    }

def parse_stenso():
    page = fetch(STENSO_URL)
    text = strip_html(page["html"])
    low = text.lower()

    sizes = [
        size for size in ["2XS", "XS", "S", "M", "L", "XL", "2XL"]
        if re.search(r"(?<![A-Za-z0-9])" + re.escape(size) + r"(?![A-Za-z0-9])", text, re.I)
    ]

    material = None
    if "78% polyester, 20% rayon, 2% spandex" in low:
        material = "78% polyester, 20% rayon, 2% spandex"
    elif "78% полиестер" in low and "20% вискоза" in low and "2% еластан" in low:
        material = "78% polyester, 20% rayon, 2% spandex"

    prices = []
    for pat, currency in [
        (r"(\d+[.,]\d{1,2})\s*(?:лв\.?|BGN)", "BGN"),
        (r"(\d+[.,]\d{1,2})\s*(?:€|EUR)", "EUR"),
    ]:
        for value in re.findall(pat, text, re.I):
            try:
                item = {"value": float(value.replace(",", ".")), "currency": currency}
                if item not in prices:
                    prices.append(item)
            except Exception:
                pass

    return {
        "source_url": page["url"],
        "observed_at_utc": page["observed_at_utc"],
        "supplier_images": [],
        "identity": {
            "brand": "Cherokee" if "cherokee" in low else None,
            "supplier_style_alias": "WWE601" if "wwe601" in low else None,
            "target_colour": "NAVY / DARK BLUE" if ("navy" in low or "dark blue" in low) else None,
            "supplier_reference": "08001931" if "08001931" in text else None,
        },
        "facts": {
            "material": material,
            "sizes_visible": sizes,
        },
        "commercial_observation": {
            "raw_price_observations": prices,
            "availability": None,
            "m99_selling_price": None,
        },
    }

def build_canonical(manufacturer, stenso, palltex=None):
    mf = manufacturer["facts"]
    sf = stenso["facts"]
    si = stenso["identity"]

    fact_merge = [
        compare_fact("material", mf.get("material"), sf.get("material")),
        {"field": "fit", "status": "MANUFACTURER_ONLY", "selected": mf.get("fit"), "authority": "manufacturer"},
        {"field": "center_back_length_inches", "status": "MANUFACTURER_ONLY", "selected": mf.get("center_back_length_inches"), "authority": "manufacturer"},
        {"field": "neckline", "status": "MANUFACTURER_ONLY", "selected": mf.get("neckline"), "authority": "manufacturer"},
        {"field": "sleeves", "status": "MANUFACTURER_ONLY", "selected": mf.get("sleeves"), "authority": "manufacturer"},
        {"field": "pockets", "status": "MANUFACTURER_ONLY", "selected": mf.get("pockets"), "authority": "manufacturer"},
        {"field": "mesh_side_panels", "status": "MANUFACTURER_ONLY", "selected": mf.get("mesh_side_panels"), "authority": "manufacturer"},
        {"field": "shirttail_hem", "status": "MANUFACTURER_ONLY", "selected": mf.get("shirttail_hem"), "authority": "manufacturer"},
        {"field": "fabric", "status": "MANUFACTURER_ONLY", "selected": mf.get("fabric"), "authority": "manufacturer"},
    ]

    conflicts = [x for x in fact_merge if x.get("status") == "SOURCE_CONFLICT"]

    return {
        "canonical_identity": {
            "brand": mf.get("brand"),
            "collection": mf.get("collection"),
            "canonical_style": mf.get("canonical_style"),
            "supplier_style_aliases": [x for x in [si.get("supplier_style_alias")] if x],
            "manufacturer_item": mf.get("manufacturer_item"),
            "target_colour": "NAVY",
            "official_name": mf.get("official_name"),
            "gender": "Women",
            "product_type": "Scrub top",
        },
        "identity_status": "CANONICAL_READY",
        "fact_merge": fact_merge,
        "commercial": {
            "manufacturer": manufacturer.get("commercial_observation", {}),
            "Stenso": stenso.get("commercial_observation", {}),
            "Palltex": palltex.get("commercial_observation") if palltex else None,
            "m99_selling_price": None,
            "operator_price_approval_required": True,
        },
        "supplier_identity": {
            "Stenso": {
                "reference": si.get("supplier_reference"),
                "style_alias": si.get("supplier_style_alias"),
                "url": stenso.get("source_url"),
            },
            "Palltex": None if palltex is None else palltex.get("identity"),
        },
        "sizes": {
            "manufacturer_official_sizes": None,
            "stenso_visible_sizes": sf.get("sizes_visible", []),
            "note": "Do not infer stock per size unless explicitly proven",
        },
        "content_evidence": {
            "ready": not conflicts,
            "allowed_claim_fields": [
                x["field"] for x in fact_merge
                if x.get("selected") not in (None, "") and x.get("status") != "SOURCE_CONFLICT"
            ],
            "blocked_conflicts": [x["field"] for x in conflicts],
            "language_targets": {"bg_sites": ["bg", "en", "ru"], "ro_sites": ["ro", "en"]},
        },
        "m99_reference_proposed": None,
        "m99_productgroup_id_proposed": None,
        "operator_review_required": True,
        "write_allowed": False,
    }
