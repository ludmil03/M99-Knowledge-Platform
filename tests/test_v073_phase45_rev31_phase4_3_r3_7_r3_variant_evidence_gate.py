from app.services.v073_phase45.calenda_public_connector import (
    _variant_evidence_summary,
    _product_price_from_variant_evidence,
    _availability_from_variant_evidence,
)

def row(size, price, a, b, c):
    return {
        "size": size,
        "price_eur": price,
        "supplier_availability": {
            "varna_qty": a,
            "delivery_1_2_days_qty": b,
            "delivery_7_10_days_qty": c,
            "total_observed_qty": a+b+c,
            "status": "IN_STOCK" if a+b+c else "OUT_OF_STOCK",
            "evidence_scope": "SUPPLIER",
            "counts_as_m99_owned_stock": False,
        },
    }

def test_river_like_evidence_derives_min_price_and_variant_availability():
    variants = [
        {"sizes": [row("S", "20.40", 0,0,207), row("XXXL*", "21.47",0,0,0)]},
        {"sizes": [row("L", "20.40", 1,0,556)]},
    ]
    s = _variant_evidence_summary(variants)
    assert s["priced_rows"] == 3
    assert s["availability_rows"] == 3
    assert s["positive_rows"] == 2
    assert _product_price_from_variant_evidence(s) == "FROM 20.40"
    assert _availability_from_variant_evidence(s) == "AVAILABLE BY VARIANT"

def test_all_zero_exact_supplier_rows_are_out_of_stock_by_variant():
    s = _variant_evidence_summary([{"sizes": [row("XXXL*", "21.47",0,0,0)]}])
    assert _availability_from_variant_evidence(s) == "OUT OF STOCK BY VARIANT"

def test_no_size_evidence_cannot_unlock_gate():
    s = _variant_evidence_summary([{"sizes": []}])
    assert s["has_price_evidence"] is False
    assert s["has_availability_evidence"] is False
    assert _product_price_from_variant_evidence(s) is None
    assert _availability_from_variant_evidence(s) is None

def test_supplier_evidence_never_counts_as_m99_owned_stock():
    r = row("L", "20.40",1,0,556)
    assert r["supplier_availability"]["counts_as_m99_owned_stock"] is False
