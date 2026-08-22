from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.v073_phase2.organization_registry import list_operator_organizations
from app.services.v073_phase2.supplier_browser import live_categories, live_products


router = APIRouter(prefix="/operator/supplier-browser", tags=["live-supplier-browser"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _database_url() -> str:
    value = os.getenv("M99_PHASE2_DATABASE_URL", "").strip()
    if not value:
        raise RuntimeError(
            "M99_PHASE2_DATABASE_URL is not configured. "
            "Production database bootstrap/migration is intentionally not automatic."
        )
    return value


def _authenticated(request: Request) -> bool:
    try:
        session = request.session
    except Exception:
        return False
    if isinstance(session, dict):
        return any(
            session.get(k)
            for k in ("user_id", "username", "user", "authenticated", "is_authenticated")
        )
    return bool(getattr(getattr(request, "state", object()), "user", None))


@router.get("", response_class=HTMLResponse)
def browser_home(request: Request):
    if not _authenticated(request):
        return RedirectResponse("/login", status_code=303)

    db = _database_url()
    return templates.TemplateResponse(
        request=request,
        name="live_supplier_browser/index.html",
        context={
            "title": "Доставчици",
            "organizations": list_operator_organizations(db),
        },
    )


@router.get("/{source_id}", response_class=HTMLResponse)
def browser_source(request: Request, source_id: str):
    if not _authenticated(request):
        return RedirectResponse("/login", status_code=303)

    db = _database_url()
    categories = live_categories(db, source_id)

    return templates.TemplateResponse(
        request=request,
        name="live_supplier_browser/source.html",
        context={
            "title": "Supplier Browser",
            "source_id": source_id,
            "categories": categories,
        },
    )


@router.get("/{source_id}/category/{category_key}", response_class=HTMLResponse)
def browser_category(
    request: Request,
    source_id: str,
    category_key: str,
    page: int = Query(1, ge=1),
):
    if not _authenticated(request):
        return RedirectResponse("/login", status_code=303)

    db = _database_url()
    products = live_products(db, source_id, category_key, page=page, limit=100)

    return templates.TemplateResponse(
        request=request,
        name="live_supplier_browser/category.html",
        context={
            "title": "Продукти от доставчика",
            "source_id": source_id,
            "category_key": category_key,
            "page": page,
            "products": products,
        },
    )
