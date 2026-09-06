from app.services.v073_phase45.calenda_public_connector import CalendaPublicConnector

p = CalendaPublicConnector().get_product("https://calenda.bg/products/31809")
assert p.supplier_reference == "93100"
assert len(p.variants) == 4

expected_source = {"20":"7","26":"206","42":"211","46":"231"}
total_rows = 0
positive_rows = 0
price_rows = 0

for v in p.variants:
    code = str(v.get("code"))
    assert code in expected_source
    assert str(v.get("source_variant_id")) == expected_source[code]
    sizes = tuple(v.get("sizes") or ())
    summary = v.get("supplier_availability")
    print(f"[LIVE VARIANT] code={code} source={v.get('source_variant_id')} sizes={len(sizes)} image={v.get('image_url')}")
    assert len(sizes) == 6, f"Expected 6 size rows for color {code}, got {len(sizes)}"
    assert summary and summary["evidence_scope"] == "SUPPLIER"
    assert summary["counts_as_m99_owned_stock"] is False

    for row in sizes:
        total_rows += 1
        price = row.get("price_eur")
        assert price is not None, f"Missing live EUR price for color={code} size={row.get('size')}"
        price_rows += 1

        # Live control product evidence: standard sizes are 20.40 EUR;
        # XXXL* is explicitly published at the higher 21.47 EUR price.
        if row["size"] == "XXXL*":
            assert price == "21.47", (code, row)
        else:
            assert price == "20.40", (code, row)

        a = row["supplier_availability"]
        assert a["counts_as_m99_owned_stock"] is False
        assert a["total_observed_qty"] == a["varna_qty"] + a["delivery_1_2_days_qty"] + a["delivery_7_10_days_qty"]
        if a["total_observed_qty"] > 0:
            positive_rows += 1

        print(
            f"  size={row['size']!r} price_eur={price!r} "
            f"varna={a['varna_qty']} d1_2={a['delivery_1_2_days_qty']} "
            f"d7_10={a['delivery_7_10_days_qty']} total={a['total_observed_qty']} status={a['status']}"
        )

assert total_rows == 24
assert price_rows == 24
assert positive_rows >= 1
assert "SIZE_AVAILABILITY_NOT_FOUND" not in p.warnings
assert "VARIANTS_NOT_DETECTED" not in p.warnings
assert "VARIANT_IMAGE_NOT_FOUND" not in p.warnings

print(f"[LIVE PASS] colors=4 size_rows={total_rows} priced_rows={price_rows} positive_rows={positive_rows}")
print("[LIVE PASS] Exact EUR size prices + supplier availability evidence confirmed.")
print("[LIVE PASS] Supplier quantities remain external evidence and are NOT M99-owned stock.")
