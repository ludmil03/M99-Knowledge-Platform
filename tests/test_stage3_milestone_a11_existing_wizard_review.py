from integrations.bultex99_supplier.models import PublicProduct
from app.services.standard_evidence_policy import StandardApplicability
from app.services.wizard_unified_review_context import build_wizard_review_context
def test_uno_context_no_publish():
 p=PublicProduct("5161","https://bultex99.com/products/5161-x","UNO LOW",supplier_sku="06100764",availability="OUT_OF_STOCK",standard="EN ISO:20345:2022+A1:2024")
 c=build_wizard_review_context(p,variant_values=("36","48"),standard_applicability=StandardApplicability.REQUIRED)
 assert c["product_evidence"]["review_ready"] is True
 assert c["product_evidence"]["supplier_product_sku"]=="06100764"
 assert c["product_evidence"]["variants"]==("36","48")
 assert c["publish_enabled"] is False and c["write_performed"] is False
def test_template_has_review_evidence_but_no_publish_action():
 from pathlib import Path
 s=Path("admin-platform/app/templates/product_import_wizard/wizard.html").read_text(encoding="utf-8")
 assert "M99_STAGE3_A11_UNIFIED_REVIEW_BEGIN" in s
 assert "product_evidence.supplier_product_sku" in s
 assert "/operator/add-products/publish" not in s
