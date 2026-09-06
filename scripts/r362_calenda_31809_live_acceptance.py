from app.services.v073_phase45.calenda_public_connector import CalendaPublicConnector

p = CalendaPublicConnector().get_product("https://calenda.bg/products/31809")
assert p.supplier_reference == "93100"
assert len(p.variants) == 4

expected = {"20":"7","26":"206","42":"211","46":"231"}
total_sizes = 0
positive = 0

for v in p.variants:
    code = str(v.get("code"))
    assert code in expected
    assert str(v.get("source_variant_id")) == expected[code]
    sizes = tuple(v.get("sizes") or ())
    summary = v.get("supplier_availability")
    print(f"[LIVE VARIANT] code={code} source={v.get('source_variant_id')} sizes={len(sizes)} image={v.get('image_url')}")
    assert sizes, f"No size evidence for color {code}"
    assert summary and summary["evidence_scope"] == "SUPPLIER"
    assert summary["counts_as_m99_owned_stock"] is False

    total_sizes += len(sizes)
    for row in sizes:
        a = row["supplier_availability"]
        assert a["counts_as_m99_owned_stock"] is False
        assert min(a["varna_qty"], a["delivery_1_2_days_qty"], a["delivery_7_10_days_qty"]) >= 0
        assert a["total_observed_qty"] == a["varna_qty"] + a["delivery_1_2_days_qty"] + a["delivery_7_10_days_qty"]
        if a["total_observed_qty"] > 0:
            positive += 1

        print(
            f"  size={row['size']!r} price_eur={row.get('price_eur')!r} "
            f"varna={a['varna_qty']} d1_2={a['delivery_1_2_days_qty']} "
            f"d7_10={a['delivery_7_10_days_qty']} total={a['total_observed_qty']} status={a['status']}"
        )

assert total_sizes >= 4
assert positive >= 1
assert "SIZE_AVAILABILITY_NOT_FOUND" not in p.warnings
assert "VARIANTS_NOT_DETECTED" not in p.warnings
assert "VARIANT_IMAGE_NOT_FOUND" not in p.warnings
print(f"[LIVE PASS] colors=4 size_rows={total_sizes} positive_rows={positive}")
print("[LIVE PASS] Supplier availability is exact external evidence and is NOT M99-owned stock.")
