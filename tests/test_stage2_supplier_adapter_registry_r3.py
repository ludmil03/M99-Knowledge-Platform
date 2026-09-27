from decimal import Decimal
import pytest
from integrations.bultex99_supplier.models import PublicProduct
from app.services.supplier_adapter_registry import registered_suppliers,get_registration
from app.services.supplier_evidence_runtime import normalize_supplier_evidence

class X:
    def __init__(self,**kw): self.__dict__.update(kw)

def test_registry_current_proven_suppliers():
    assert registered_suppliers()==("BULTEX99","CALENDA","PALLTEX")

def test_unknown_means_unregistered_not_forbidden_future_supplier():
    with pytest.raises(ValueError,match="SUPPLIER_NOT_REGISTERED:FEYA"):
        get_registration("feya")

def test_bultex_registry_runtime():
    p=PublicProduct("5161","https://bultex99.com/product/5161","UNO LOW",
      supplier_sku="06100764.36",gross_price_eur=Decimal("58.90"),brand="Panda")
    assert normalize_supplier_evidence("bultex99",p).supplier_key=="BULTEX99"

def test_calenda_registry_runtime():
    h=X(source_key="31809",url="https://calenda.bg/products/31809",name="Observed",
      supplier_reference="MF31809",brand="Observed",images=(),price_text="10",
      availability_text="IN_STOCK",currency="EUR",variants=(),warnings=(),calenda_product_id="31809")
    assert normalize_supplier_evidence("calenda",h).supplier_key=="CALENDA"

def test_palltex_registry_runtime():
    h=X(source_key="100018",url="https://palltex.bg/bg/p/x/123",name="BWolf",
      supplier_reference="BW123",brand="BWolf",images=(),price_text="20",
      availability_text="IN_STOCK",currency="BGN",variants=(),warnings=())
    assert normalize_supplier_evidence("palltex",h).supplier_key=="PALLTEX"
