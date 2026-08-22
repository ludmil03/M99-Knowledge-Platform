from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.v073_phase3.product_presence import product_to_targets, target_to_products


router = APIRouter(prefix="/operator/presence", tags=["product-presence"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _database_url() -> str:
    value = os.getenv("M99_PHASE3_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError(
            "M99_PHASE3_DATABASE_URL is not configured. "
            "Production database migration remains a separate approved milestone."
        )
    return value


def _authenticated(request: Request) -> bool:
    try:
        session = request.session
    except Exception:
        return False
    if isinstance(session, dict):
        return any(session.get(k) for k in ("user_id","username","user","authenticated","is_authenticated"))
    return False


@router.get("", response_class=HTMLResponse)
def presence_home(
    request: Request,
    product_id: str | None = Query(None),
    target: str | None = Query(None),
):
    if not _authenticated(request):
        return RedirectResponse("/login", status_code=303)

    db = _database_url()
    rows = []
    mode = "EMPTY"
    if product_id:
        rows = product_to_targets(db, product_id)
        mode = "PRODUCT_TO_TARGETS"
    elif target:
        rows = target_to_products(db, target)
        mode = "TARGET_TO_PRODUCTS"

    return templates.TemplateResponse(
        request=request,
        name="product_presence/index.html",
        context={
            "title": "Product Presence",
            "mode": mode,
            "rows": rows,
            "product_id": product_id,
            "target": target,
        },
    )
