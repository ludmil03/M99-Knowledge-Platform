from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from .models import PublicProduct,IdentityPreview,DryRunItem,DryRunReport

MODES={"one_product","multiple_products","one_category","multiple_categories",
       "all_products","first_n","only_new_to_m99","manual_selection"}

@dataclass(frozen=True)
class SelectionRequest:
    mode:str
    product_refs:tuple[str,...]=()
    category_refs:tuple[str,...]=()
    first_n:int|None=None

def validate_selection(r:SelectionRequest)->None:
    if r.mode not in MODES: raise ValueError("Invalid selection mode")
    if r.mode=="one_product" and len(r.product_refs)!=1: raise ValueError("one_product requires exactly one product")
    if r.mode=="multiple_products" and len(r.product_refs)<2: raise ValueError("multiple_products requires >=2 products")
    if r.mode=="one_category" and len(r.category_refs)!=1: raise ValueError("one_category requires exactly one category")
    if r.mode=="multiple_categories" and len(r.category_refs)<2: raise ValueError("multiple_categories requires >=2 categories")
    if r.mode=="first_n" and (r.first_n is None or r.first_n<=0): raise ValueError("first_n requires positive N")

def select_products(r:SelectionRequest,products:Iterable[PublicProduct],
                    identities:dict[str,IdentityPreview]|None=None)->list[PublicProduct]:
    validate_selection(r); xs=list(products); ids=identities or {}
    if r.mode in {"one_product","multiple_products","manual_selection"}:
      wanted=set(r.product_refs); xs=[p for p in xs if p.supplier_product_id in wanted or p.source_url in wanted]
    elif r.mode in {"one_category","multiple_categories"}:
      wanted=set(r.category_refs); xs=[p for p in xs if wanted.intersection(p.category_refs)]
    elif r.mode=="first_n": xs=xs[:r.first_n]
    elif r.mode=="only_new_to_m99":
      xs=[p for p in xs if ids.get(p.supplier_product_id,IdentityPreview(p.supplier_product_id,"NEW")).status=="NEW"]
    return xs

def resolve_targets(requested:Iterable[str],registry:dict[str,tuple[bool,bool]])->tuple[list[str],list[str],list[str],list[str]]:
    req=list(dict.fromkeys(x for x in requested if x)); auth=[];ready=[];blocked=[]
    for x in req:
      a,r=registry.get(x,(False,False))
      if a: auth.append(x)
      if a and r: ready.append(x)
      else: blocked.append(x)
    return req,auth,ready,blocked

def qa(p:PublicProduct,identity:IdentityPreview)->tuple[str,list[str]]:
    e=[]
    if not p.name.strip(): e.append("NAME_MISSING")
    if not p.supplier_product_id: e.append("SUPPLIER_ID_MISSING")
    if identity.status in {"AMBIGUOUS","UNRESOLVED"}: e.append("IDENTITY_"+identity.status)
    return ("READY" if not e else "BLOCKED"),e

def build_dry_run(selection:SelectionRequest,products:Iterable[PublicProduct],
                  identities:dict[str,IdentityPreview],requested_targets:Iterable[str],
                  target_registry:dict[str,tuple[bool,bool]])->DryRunReport:
    selected=select_products(selection,products,identities)
    req,auth,ready,blocked=resolve_targets(requested_targets,target_registry)
    items=[]
    for p in selected:
      ident=identities.get(p.supplier_product_id,IdentityPreview(p.supplier_product_id,"NEW",("no canonical match",)))
      status,errors=qa(p,ident)
      items.append(DryRunItem(p.supplier_product_id,p.source_url,p.name,ident.status,status,errors))
    return DryRunReport("BULTEX99_PUBLIC",selection.mode,len(selected),req,auth,ready,blocked,items,False)
