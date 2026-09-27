from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Iterable, Mapping, Any

SUPPORTED_SELECTION_MODES = (
    "one_product","multiple_products","one_category","multiple_categories",
    "all_products","first_n","only_new_to_m99","manual_selection",
)

@dataclass(frozen=True)
class ResolvedSelection:
    mode: str
    product_urls: tuple[str,...]
    discovery_pages: int
    blockers: tuple[str,...]
    write_performed: bool = False

@dataclass(frozen=True)
class ProductReviewItem:
    source_url: str
    status: str
    context: Mapping[str,Any] | None
    blocker: str | None

@dataclass(frozen=True)
class MultiSelectionReview:
    selection: ResolvedSelection
    items: tuple[ProductReviewItem,...]
    ready_count: int
    blocked_count: int
    publish_enabled: bool = False
    write_performed: bool = False

def _unique(values: Iterable[str]) -> tuple[str,...]:
    out=[]; seen=set()
    for raw in values:
        v=str(raw or "").strip()
        if v and v not in seen:
            seen.add(v); out.append(v)
    return tuple(out)

def resolve_selection(
    mode:str, *,
    product_refs:Iterable[str]=(),
    category_refs:Iterable[str]=(),
    first_n:int|None=None,
    discover_category:Callable[[str],Iterable[str]]|None=None,
    discover_all:Callable[[],Iterable[str]]|None=None,
    only_new:Callable[[Iterable[str]],Iterable[str]]|None=None,
) -> ResolvedSelection:
    if mode not in SUPPORTED_SELECTION_MODES:
        return ResolvedSelection(mode,(),0,("UNSUPPORTED_SELECTION_MODE",))
    products=_unique(product_refs); cats=_unique(category_refs); pages=0
    if mode=="one_product":
        if len(products)!=1:return ResolvedSelection(mode,(),0,("ONE_PRODUCT_REQUIRES_EXACTLY_ONE",))
    elif mode in ("multiple_products","manual_selection"):
        if not products:return ResolvedSelection(mode,(),0,("PRODUCT_SELECTION_EMPTY",))
    elif mode in ("one_category","multiple_categories"):
        expected=1 if mode=="one_category" else None
        if (expected==1 and len(cats)!=1) or (expected is None and not cats):
            return ResolvedSelection(mode,(),0,("CATEGORY_SELECTION_INVALID",))
        if discover_category is None:return ResolvedSelection(mode,(),0,("CATEGORY_DISCOVERY_NOT_PROVEN",))
        found=[]
        for c in cats:
            pages+=1; found.extend(discover_category(c))
        products=_unique(found)
    elif mode in ("all_products","first_n","only_new_to_m99"):
        if discover_all is None:return ResolvedSelection(mode,(),0,("SITE_DISCOVERY_NOT_PROVEN",))
        pages+=1; products=_unique(discover_all())
        if mode=="first_n":
            if not first_n or first_n<1:return ResolvedSelection(mode,(),pages,("FIRST_N_INVALID",))
            products=products[:first_n]
        elif mode=="only_new_to_m99":
            if only_new is None:return ResolvedSelection(mode,(),pages,("ONLY_NEW_FILTER_NOT_PROVEN",))
            products=_unique(only_new(products))
    if not products:return ResolvedSelection(mode,(),pages,("RESOLVED_SELECTION_EMPTY",))
    return ResolvedSelection(mode,products,pages,())

def build_multi_selection_review(
    selection:ResolvedSelection, *,
    review_one:Callable[[str],Mapping[str,Any]],
    max_products_per_batch:int=50,
) -> MultiSelectionReview:
    if selection.blockers:
        return MultiSelectionReview(selection,(),0,0,False,False)
    if max_products_per_batch<1: raise ValueError("BATCH_LIMIT_INVALID")
    items=[]
    for start in range(0,len(selection.product_urls),max_products_per_batch):
        for url in selection.product_urls[start:start+max_products_per_batch]:
            try:
                ctx=review_one(url)
                blockers=tuple((ctx.get("product_evidence") or {}).get("blockers") or ())
                items.append(ProductReviewItem(url,"BLOCKED" if blockers else "READY",ctx,",".join(blockers) or None))
            except Exception as exc:
                items.append(ProductReviewItem(url,"BLOCKED",None,type(exc).__name__))
    ready=sum(x.status=="READY" for x in items)
    blocked=len(items)-ready
    return MultiSelectionReview(selection,tuple(items),ready,blocked,False,False)
