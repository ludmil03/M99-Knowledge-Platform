from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.supplier_evidence_runtime import normalize_supplier_evidence, supported_suppliers

class X:
    def __init__(self,**kw): self.__dict__.update(kw)

def test_registry_is_exact_three_supplier_contract():
    assert supported_suppliers()==("BULTEX99","CALENDA","PALLTEX")

def test_runtime_bultex_uno_low():
    p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
        supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda",
        standard="EN ISO 20345:2022+A1:2024")
    e=normalize_supplier_evidence("bultex99",p)
    assert e.supplier_key=="BULTEX99"
    assert e.identity_facts["supplier_sku"].value=="06100764.36"

def test_runtime_calenda_variant_evidence():
    h=X(source_key="31809",url="https://calenda.bg/products/31809",name="Observed",
        supplier_reference="MF31809",brand="Observed",images=("https://calenda.bg/i/a.jpg",),
        price_text="10",availability_text="IN_STOCK",currency="EUR",
        variants=({"type":"COLOR","code":"7","image_url":"https://calenda.bg/i/red.jpg"},),
        warnings=(),calenda_product_id="31809")
    e=normalize_supplier_evidence("CALENDA",h)
    assert e.variants[0]["code"]=="7"

def test_runtime_palltex_identity_evidence():
    h=X(source_key="100018",url="https://palltex.bg/bg/p/x/123",name="BWolf",
        supplier_reference="BW123",brand="BWolf",images=(),price_text="20",
        availability_text="IN_STOCK",currency="BGN",variants=(),warnings=())
    e=normalize_supplier_evidence("PALLTEX",h)
    assert e.identity_facts["supplier_reference"].value=="BW123"

def test_unsupported_supplier_fails_closed_no_fourth_importer():
    with pytest.raises(ValueError,match="UNSUPPORTED_SUPPLIER"):
        normalize_supplier_evidence("FOURTH",object())

def test_invalid_evidence_fails_closed():
    h=X(source_key="",url="",name="",supplier_reference=None,brand=None,images=(),
        price_text=None,availability_text=None,currency=None,variants=(),warnings=())
    with pytest.raises(ValueError,match="INVALID_SUPPLIER_EVIDENCE"):
        normalize_supplier_evidence("CALENDA",h)
