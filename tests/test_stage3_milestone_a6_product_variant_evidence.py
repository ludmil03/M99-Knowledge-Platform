from integrations.bultex99_supplier.models import PublicProduct
from app.services.product_variant_evidence_gate import *
def test_product_sku_and_size_are_separate():
 p=PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764",gross_price_eur=None,availability="OUT_OF_STOCK",standard="EN ISO 20345:2022+A1:2024")
 r=build_product_variant_evidence(p,variant_values=("36","37","48"))
 assert r.supplier_product_sku=="06100764"
 assert [v.value for v in r.variants]==["36","37","48"]
 assert r.can_continue_to_content and not r.blockers and r.write_performed is False
def test_missing_standard_blocks_without_invention():
 p=PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764",availability="OUT_OF_STOCK",standard=None)
 r=build_product_variant_evidence(p,variant_values=("36",))
 assert "TECHNICAL_STANDARD_MISSING" in r.blockers
 assert r.standard is None and not r.can_continue_to_content
def test_fused_variant_identity_blocks():
 p=PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764.36",standard="EN ISO 20345:2022+A1:2024")
 r=build_product_variant_evidence(p)
 assert "PRODUCT_VARIANT_IDENTITY_FUSED" in r.blockers and not r.can_continue_to_content
def test_out_of_stock_is_preserved_not_rewritten():
 p=PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764",availability="OUT_OF_STOCK",standard="EN ISO 20345:2022+A1:2024")
 assert build_product_variant_evidence(p).availability=="OUT_OF_STOCK"
