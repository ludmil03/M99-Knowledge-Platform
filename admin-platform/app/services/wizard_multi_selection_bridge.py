from __future__ import annotations
from typing import Callable, Any
from app.services.multi_selection_orchestration import resolve_selection, build_multi_selection_review

def build_existing_wizard_multi_review(
    draft: Any, *,
    discover_category: Callable[[str], list[str]] | None = None,
    discover_all: Callable[[], list[str]] | None = None,
    only_new: Callable[[list[str]], list[str]] | None = None,
    review_one: Callable[[str], dict] | None = None,
    max_products_per_batch: int = 50,
) -> dict:
    mode=str(draft.selection_mode or "")
    selection=resolve_selection(
        mode,
        product_refs=draft.selected_product_refs,
        category_refs=draft.selected_category_refs,
        first_n=draft.first_n,
        discover_category=discover_category,
        discover_all=discover_all,
        only_new=only_new,
    )
    if selection.blockers or review_one is None:
        return {
            "multi_selection": selection,
            "multi_review": None,
            "selection_blockers": selection.blockers or ("REVIEW_ADAPTER_NOT_PROVEN",),
            "publish_enabled": False,
            "write_performed": False,
        }
    review=build_multi_selection_review(
        selection,review_one=review_one,max_products_per_batch=max_products_per_batch)
    return {
        "multi_selection": selection,
        "multi_review": review,
        "selection_blockers": (),
        "publish_enabled": False,
        "write_performed": False,
    }
