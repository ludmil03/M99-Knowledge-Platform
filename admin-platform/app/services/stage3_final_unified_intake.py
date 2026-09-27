from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Iterable, Mapping
from app.services.wizard_multi_selection_bridge import build_existing_wizard_multi_review

@dataclass(frozen=True)
class Stage3FinalResult:
    selection_mode: str
    resolved_count: int
    ready_count: int
    blocked_count: int
    selection_blockers: tuple[str,...]
    requested_targets: tuple[str,...]
    ready_targets: tuple[str,...]
    blocked_targets: tuple[str,...]
    publish_enabled: bool = False
    write_performed: bool = False

def build_stage3_final_review(
    draft: Any, *,
    discover_category: Callable[[str], Iterable[str]] | None = None,
    discover_all: Callable[[], Iterable[str]] | None = None,
    only_new: Callable[[Iterable[str]], Iterable[str]] | None = None,
    review_one: Callable[[str], Mapping[str,Any]] | None = None,
    max_products_per_batch: int = 50,
) -> tuple[Stage3FinalResult, dict[str,Any]]:
    ctx=build_existing_wizard_multi_review(
        draft, discover_category=discover_category, discover_all=discover_all,
        only_new=only_new, review_one=review_one,
        max_products_per_batch=max_products_per_batch,
    )
    sel=ctx["multi_selection"]; rev=ctx["multi_review"]
    result=Stage3FinalResult(
        selection_mode=str(draft.selection_mode or ""),
        resolved_count=len(sel.product_urls),
        ready_count=0 if rev is None else rev.ready_count,
        blocked_count=0 if rev is None else rev.blocked_count,
        selection_blockers=tuple(ctx["selection_blockers"]),
        requested_targets=tuple(draft.requested_targets),
        ready_targets=tuple(draft.ready_targets),
        blocked_targets=tuple(draft.blocked_targets),
        publish_enabled=False, write_performed=False,
    )
    return result,ctx
