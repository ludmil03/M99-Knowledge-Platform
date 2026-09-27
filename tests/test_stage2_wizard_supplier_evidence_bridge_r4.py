from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.wizard_supplier_evidence_bridge import build_wizard_evidence_preview

class X:
    def __init__(self,**kw): self.__dict__.update(kw)

def test_bultex_wizard_preview_is_read_only():
    p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
      supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda",
      standard="EN ISO 20345:2022+A1:2024")
    r=build_wizard_evidence_preview("BULTEX99",[p])
    assert r["count"]==1 and r["write_performed"] is False
    assert r["items"][0]["identity"]["supplier_sku"]=="06100764.36"

def test_calenda_wizard_preview_preserves_variant_counts():
    h=X(source_key="31809",url="https://calenda.bg/products/31809",name="Observed",
      supplier_reference="MF31809",brand="Observed",images=("https://calenda.bg/a.jpg",),
      price_text="10",availability_text="IN_STOCK",currency="EUR",
      variants=({"type":"COLOR","code":"7"},),warnings=(),calenda_product_id="31809")
    r=build_wizard_evidence_preview("CALENDA",[h])
    assert r["items"][0]["variant_count"]==1 and r["write_performed"] is False

def test_palltex_wizard_preview_preserves_reference():
    h=X(source_key="100018",url="https://palltex.bg/bg/p/x/123",name="BWolf",
      supplier_reference="BW123",brand="BWolf",images=(),price_text="20",
      availability_text="IN_STOCK",currency="BGN",variants=(),warnings=())
    r=build_wizard_evidence_preview("PALLTEX",[h])
    assert r["items"][0]["identity"]["supplier_reference"]=="BW123"

def test_unregistered_supplier_fails_closed_through_wizard_bridge():
    with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
        build_wizard_evidence_preview("FEYA",[object()])

def test_empty_batch_is_no_write():
    r=build_wizard_evidence_preview("BULTEX99",[])
    assert r["count"]==0 and r["write_performed"] is False
