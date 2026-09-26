from __future__ import annotations
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router=APIRouter(prefix="/operator/add-products/bultex99",tags=["operator-product-import"])

@router.get("/contract")
def contract(request:Request):
    return JSONResponse({
      "source":"BULTEX99_PUBLIC",
      "mode":"READ_ONLY_DRY_RUN",
      "selection_modes":["one_product","multiple_products","one_category","multiple_categories","all_products","first_n","only_new_to_m99","manual_selection"],
      "identity_states":["NEW","EXISTING","AMBIGUOUS","UNRESOLVED"],
      "write_performed":False,
      "network_required_for_tests":False,
    })
