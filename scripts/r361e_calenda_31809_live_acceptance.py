from app.services.v073_phase45.calenda_public_connector import CalendaPublicConnector

EXPECTED = {
    "20": ("БЯЛ", "7"),
    "26": ("черно", "206"),
    "42": ("тъмно-синьо", "211"),
    "46": ("небесно-синьо", "231"),
}

p = CalendaPublicConnector().get_product("https://calenda.bg/products/31809")
variants = list(p.variants)

print(f"[LIVE] name={p.name!r} sku={p.supplier_reference!r} variants={len(variants)}")
for v in variants:
    print(
        f"[LIVE VARIANT] code={v.get('code')} label={v.get('value')!r} "
        f"source_variant_id={v.get('source_variant_id')} "
        f"image={v.get('image_url')!r} url={v.get('url')!r}"
    )

assert len(variants) == 4, f"Expected 4 variants, got {len(variants)}"
by_code = {str(v.get("code")): v for v in variants}
assert set(by_code) == set(EXPECTED), f"Unexpected codes: {set(by_code)}"

for code, (label, source_id) in EXPECTED.items():
    v = by_code[code]
    assert str(v.get("source_variant_id")) == source_id, (code, v)
    assert str(v.get("value", "")).casefold() == label.casefold(), (code, v)
    assert v.get("image_url"), f"Variant {code} has no image"

images = [v["image_url"] for v in variants]
assert len(set(images)) == 4, f"Expected 4 distinct variant images, got {images}"
assert "VARIANTS_NOT_DETECTED" not in p.warnings
assert "VARIANT_IMAGE_NOT_FOUND" not in p.warnings
print("[LIVE PASS] 4 exact GET variants and 4 distinct per-variant images.")
