import pytest
from dataclasses import dataclass
from app.services.wizard_hydration_capability import *
from integrations.bultex99_supplier.models import PublicProduct
@dataclass(frozen=True)
class R:
    product:PublicProduct
    write_performed:bool=False
def p(u): return PublicProduct("5161",u,"Panda UNO LOW",supplier_sku="06100764.36")
def test_bultex_runtime_preserves_order():
    calls=[]
    refs=["https://bultex99.com/products/5161-uno-low","https://bultex99.com/products/5162-two"]
    out=hydrate_for_wizard("org-bultex",refs,runtime_call=lambda u:(calls.append(u) or R(p(u))))
    assert calls==refs and [x.source_url for x in out]==refs
def test_bad_result_fails_closed():
    with pytest.raises(ValueError,match="HYDRATION_RESULT_INVALID"):
        hydrate_for_wizard("org-bultex",["x"],runtime_call=lambda u:object())
def test_write_invariant_fails_closed():
    @dataclass(frozen=True)
    class Bad:
        product:PublicProduct
        write_performed:bool=True
    with pytest.raises(ValueError,match="HYDRATION_WRITE_INVARIANT_FAILED"):
        hydrate_for_wizard("org-bultex",["x"],runtime_call=lambda u:Bad(p(u)))
