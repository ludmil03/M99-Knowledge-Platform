from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT/"admin-platform/app/services/v073_phase45/r37_import_bridge.py"
ROUTER = ROOT/"admin-platform/app/routers/r37_add_products_flow.py"
PREPARE = ROOT/"admin-platform/app/templates/add_products/r37_prepare.html"
PREVIEW = ROOT/"admin-platform/app/templates/add_products/r37_canonical_preview.html"

def replace_once(path, old, new):
    text = path.read_text(encoding="utf-8")
    if new in text:
        return
    if old not in text:
        raise RuntimeError(f"R7 patch anchor not found in {path}")
    path.write_text(text.replace(old, new, 1), encoding="utf-8")

replace_once(ROUTER,
'    target: str = Form(...),\n    db: Session = Depends(get_db),\n):',
'    target: str = Form(...),\n    manufacturer_name: str = Form(""),\n    db: Session = Depends(get_db),\n):')

replace_once(ROUTER,
'            product_url=product_url,\n            target=target,\n        )',
'            product_url=product_url,\n            target=target,\n            manufacturer_name=manufacturer_name,\n        )')

replace_once(BRIDGE,
'    product_url: str,\n    target: str,\n):',
'    product_url: str,\n    target: str,\n    manufacturer_name: str = "",\n):')

replace_once(BRIDGE,
'    identity = resolve_identity(\n        _database_url(db),\n        IncomingIdentity(',
'    confirmed_manufacturer = (manufacturer_name or hydrated.brand or "").strip()\n\n    identity = resolve_identity(\n        _database_url(db),\n        IncomingIdentity(')

replace_once(BRIDGE,
'            brand_name=hydrated.brand,\n        ),',
'            brand_name=confirmed_manufacturer or hydrated.brand,\n        ),')

replace_once(BRIDGE,
'        "supplier_reference": hydrated.supplier_reference or "",\n    }',
'        "supplier_reference": hydrated.supplier_reference or "",\n        "manufacturer_name": confirmed_manufacturer,\n        "manufacturer_evidence_scope": "OPERATOR_CONFIRMED_SUPPLIER_EVIDENCE",\n    }')

replace_once(BRIDGE,
'    return {\n        "url": hydrated.url,',
'    variant_images = []\n    variant_image_evidence = []\n    for variant in (hydrated.variants or ()):\n        image_url = str(variant.get("image_url") or "").strip()\n        if image_url and image_url not in variant_images:\n            variant_images.append(image_url)\n        if image_url:\n            variant_image_evidence.append({\n                "code": str(variant.get("code") or ""),\n                "value": str(variant.get("value") or variant.get("label") or ""),\n                "image_url": image_url,\n            })\n    all_images = []\n    for image_url in list(hydrated.images or ()) + variant_images:\n        if image_url and image_url not in all_images:\n            all_images.append(image_url)\n\n    return {\n        "url": hydrated.url,')

replace_once(BRIDGE,
'        "images": list(hydrated.images or ()),\n        "description": hydrated.description or "",',
'        "images": all_images,\n        "variant_images": variant_images,\n        "variant_image_evidence": variant_image_evidence,\n        "manufacturer_name": hydrated.brand or "",\n        "manufacturer_evidence_scope": "SUPPLIER_EVIDENCE_UNTIL_OPERATOR_CONFIRMED",\n        "description": hydrated.description or "",')

replace_once(PREPARE,
'    {% for t in targets %}\n      <label style="display:block;margin:8px 0">',
'    <div class="card" style="margin:12px 0">\n      <h3>Manufacturer Evidence</h3>\n      <label>Производител / Brand\n        <input type="text" name="manufacturer_name" value="{{ hydrated.brand or \'\' }}"\n               placeholder="напр. PROMO STARS" style="width:100%;max-width:520px;padding:8px;margin-top:6px">\n      </label>\n      <p><small>Предложено от supplier evidence. Операторът може да потвърди или коригира.\n      Това не създава автоматично approved Manufacturer.</small></p>\n    </div>\n    {% for t in targets %}\n      <label style="display:block;margin:8px 0">')

replace_once(PREPARE,
'  <p>Variants: {{ hydrated.variants|length }}</p>',
'  <p>Variants: {{ hydrated.variants|length }}</p>\n  {% if hydrated.variants %}\n  <h3>Variant image evidence</h3>\n  <div style="display:flex;gap:14px;flex-wrap:wrap">\n    {% for v in hydrated.variants %}\n      <div style="width:150px">\n        {% if v.image_url %}\n          <img src="{{ v.image_url }}" alt="{{ v.value or v.label or v.code }}"\n               style="width:140px;height:140px;object-fit:contain;border:1px solid #ddd">\n        {% else %}<div class="warn">Няма снимка</div>{% endif %}\n        <div><b>{{ v.value or v.label or ("Color " ~ v.code) }}</b></div>\n        <div><small>code {{ v.code }}</small></div>\n      </div>\n    {% endfor %}\n  </div>\n  {% endif %>')

replace_once(PREVIEW,
'<h2>Canonical payload preview</h2>',
'<h2>Manufacturer evidence</h2>\n<p><b>{{ supplier_product.manufacturer_name or "—" }}</b></p>\n<p><small>{{ supplier_product.manufacturer_evidence_scope }}</small></p>\n<h2>Variant image evidence</h2>\n{% if supplier_product.variant_image_evidence %}\n<div style="display:flex;gap:14px;flex-wrap:wrap">\n{% for img in supplier_product.variant_image_evidence %}\n  <div style="width:160px">\n    <img src="{{ img.image_url }}" alt="{{ img.value or img.code }}"\n         style="width:150px;height:150px;object-fit:contain;border:1px solid #ddd">\n    <div><b>{{ img.value or ("Color " ~ img.code) }}</b></div>\n  </div>\n{% endfor %}\n</div>\n{% else %}<div class="warn">Няма variant image evidence.</div>{% endif %}\n<h2>Canonical payload preview</h2>')
print("[PASS] R3.7R7 runtime patch applied.")
