from __future__ import annotations
from dataclasses import asdict
from integrations.bultex99_supplier.models import PublicProduct, IdentityPreview
from integrations.bultex99_supplier.pipeline import SelectionRequest, build_dry_run

BULTEX_ORG_ID="org-bultex"

def is_bultex_source(organization_id: str|None)->bool:
    return organization_id==BULTEX_ORG_ID

def build_bultex_dry_run(*, selection_mode:str, product_refs:list[str], category_refs:list[str],
                         first_n:int|None, products:list[PublicProduct],
                         identities:dict[str,IdentityPreview], requested_targets:list[str],
                         target_registry:dict[str,tuple[bool,bool]])->dict:
    req=SelectionRequest(selection_mode,tuple(product_refs),tuple(category_refs),first_n)
    return build_dry_run(req,products,identities,requested_targets,target_registry).as_dict()

def identity_summary(report:dict)->str:
    counts={}
    for item in report["items"]:
        s=item["identity_status"]; counts[s]=counts.get(s,0)+1
    return " / ".join(f"{k}: {counts[k]}" for k in ("NEW","EXISTING","AMBIGUOUS","UNRESOLVED") if counts.get(k)) or "Няма избрани продукти"
