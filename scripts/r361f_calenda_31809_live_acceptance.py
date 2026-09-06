from app.services.v073_phase45.calenda_public_connector import CalendaPublicConnector

URL = "https://calenda.bg/products/31809"
EXPECTED = {
    "20": ("7", "https://calenda.bg/storage/products/93100_20a.jpg"),
    "26": ("206", "https://calenda.bg/storage/products/93100_26a.jpg"),
    "42": ("211", "https://calenda.bg/storage/products/93100_42a.jpg"),
    "46": ("231", "https://calenda.bg/storage/products/93100_46a.jpg"),
}

p = CalendaPublicConnector().get_product(URL)
print(f"[LIVE] name={p.name!r} sku={p.supplier_ref!r} variants={len(p.variants)}")
assert len(p.variants) == 4, p.variants

images = []
for v in p.variants:
    code = str(v.get("code"))
    sid, expected_image = EXPECTED[code]
    print(f"[LIVE VARIANT] code={code} label={v.get('value')!r} source_variant_id={v.get('source_variant_id')} image={v.get('image_url')!r}")
    assert str(v.get("source_variant_id")) == sid
    assert v.get("image_url") == expected_image
    images.append(v.get("image_url"))

assert len(set(images)) == 4
assert "VARIANTS_NOT_DETECTED" not in p.warnings
assert "VARIANT_IMAGE_NOT_FOUND" not in p.warnings
print("[LIVE PASS] Exact Calenda color -> source GET id -> distinct product image evidence confirmed.")
