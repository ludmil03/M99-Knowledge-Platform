from decimal import Decimal
from integrations.bultex99_supplier.models import PublicProduct
from app.services.supplier_product_evidence import SupplierProductEvidence
from app.services.supplier_evidence_adapters import from_bultex99, from_calenda, from_palltex

class X:
    def __init__(self,**kw): self.__dict__.update(kw)

def test_bultex_contract_uno_low_shape():
    p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",supplier_sku="06100764.36",
                    gross_price_eur=Decimal("58.90"),availability="visible",brand="Panda",
                    standard="EN ISO 20345:2022+A1:2024")
    e=from_bultex99(p)
    assert isinstance(e,SupplierProductEvidence)
    assert e.supplier_key=="BULTEX99" and e.identity_facts["supplier_sku"].value=="06100764.36"
    assert e.technical_facts["standard"].value=="EN ISO 20345:2022+A1:2024"
    assert e.validate()==()

def test_calenda_preserves_variant_image_evidence():
    h=X(source_key="31809",url="https://calenda.bg/products/31809",name="Observed product",
        supplier_reference="MF31809",brand="Observed",images=("https://calenda.bg/i/a.jpg",),
        price_text="10.00",availability_text="IN_STOCK",currency="EUR",
        variants=({"type":"COLOR","code":"7","image_url":"https://calenda.bg/i/red.jpg","sizes":[{"size":"M"}]},),
        warnings=(),calenda_product_id="31809")
    e=from_calenda(h)
    assert e.variants[0]["code"]=="7"
    assert e.variants[0]["image_url"].endswith("red.jpg")
    assert e.availability.value=="IN_STOCK"
    assert e.validate()==()

def test_palltex_preserves_supplier_reference_and_variants():
    h=X(source_key="100018",url="https://palltex.bg/bg/p/example/123",name="BWolf product",
        supplier_reference="BW123",brand="BWolf",images=("https://palltex.bg/img/a.jpg",),
        price_text="20",availability_text="IN_STOCK",currency="BGN",
        variants=({"type":"COLOR_SIZE","code":"BW123","sizes":[{"size":"L","availability_semantics":"EXTERNAL_SUPPLIER_SELECTION_EVIDENCE_NOT_M99_STOCK"}]},),
        warnings=())
    e=from_palltex(h)
    assert e.identity_facts["supplier_reference"].value=="BW123"
    assert "EXTERNAL_SUPPLIER" in e.variants[0]["sizes"][0]["availability_semantics"]
    assert e.validate()==()

def test_contract_fail_closed_without_identity():
    e=SupplierProductEvidence("X","k","https://example.invalid")
    assert "IDENTITY_FACTS_MISSING" in e.validate()
