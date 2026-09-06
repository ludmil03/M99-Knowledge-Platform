from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.v073_phase45.unified_add_products import (
    SourceDiscoveryError,
    approved_categories,
    approved_sources,
    connector_status,
    hydrate_product,
    list_category_products,
    list_source_categories,
    require_source,
)

router = APIRouter(prefix="/add-products", tags=["Unified Add Products"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def C(request, db, **x):
    data = {
        "request": request,
        "sources": approved_sources(db),
        "canonical_categories": approved_categories(db),
        "selected_source": None,
        "categories": [],
        "selected_category": None,
        "products": [],
        "hydrated": None,
        "error": None,
        "connector": None,
        "current_category_url": "",
    }
    data.update(x)
    return data


def _selected_source_context(db: Session, source_uuid: str):
    source = require_source(db, source_uuid)
    status = connector_status(source)
    categories = list_source_categories(source) if status.state == "READY" else []
    return source, status, categories


def _find_category(categories, category_url: str):
    target = (category_url or "").rstrip("/")
    for category in categories:
        if str(category.url).rstrip("/") == target:
            return category
    return None


def _render_category(
    request: Request,
    db: Session,
    source_uuid: str,
    category_url: str,
    hydrated=None,
):
    source, status, categories = _selected_source_context(db, source_uuid)
    selected_category = _find_category(categories, category_url)
    products = list_category_products(source, category_url)
    return templates.TemplateResponse(
        "add_products/workspace.html",
        C(
            request,
            db,
            selected_source=source,
            connector=status,
            categories=categories,
            selected_category=selected_category,
            products=products,
            hydrated=hydrated,
            current_category_url=category_url,
        ),
    )


@router.get("", response_class=HTMLResponse)
def home(
    request: Request,
    source_uuid: str | None = Query(default=None),
    category_url: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    if not source_uuid:
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(request, db),
        )
    try:
        if category_url:
            return _render_category(request, db, source_uuid, category_url)

        source, status, categories = _selected_source_context(db, source_uuid)
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(
                request,
                db,
                selected_source=source,
                connector=status,
                categories=categories,
            ),
        )
    except SourceDiscoveryError as exc:
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(request, db, error=str(exc)),
            status_code=400,
        )


@router.post("/source")
def source(
    source_uuid: str = Form(...),
    db: Session = Depends(get_db),
):
    require_source(db, source_uuid)
    return RedirectResponse(
        url=f"/add-products?source_uuid={quote(source_uuid)}",
        status_code=303,
    )


@router.get("/category", response_class=HTMLResponse)
def category_get(
    request: Request,
    source_uuid: str = Query(...),
    category_url: str = Query(...),
    db: Session = Depends(get_db),
):
    try:
        return _render_category(request, db, source_uuid, category_url)
    except SourceDiscoveryError as exc:
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(request, db, error=str(exc)),
            status_code=400,
        )


@router.post("/category")
def category(
    source_uuid: str = Form(...),
    category_url: str = Form(...),
    db: Session = Depends(get_db),
):
    require_source(db, source_uuid)
    return RedirectResponse(
        url=(
            f"/add-products/category"
            f"?source_uuid={quote(source_uuid)}"
            f"&category_url={quote(category_url, safe='')}"
        ),
        status_code=303,
    )


@router.post("/hydrate", response_class=HTMLResponse)
def hydrate(
    request: Request,
    source_uuid: str = Form(...),
    product_url: str = Form(...),
    category_url: str = Form(""),
    db: Session = Depends(get_db),
):
    try:
        source, status, categories = _selected_source_context(db, source_uuid)
        selected_category = _find_category(categories, category_url) if category_url else None
        products = list_category_products(source, category_url) if category_url else []
        hydrated = hydrate_product(source, product_url)
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(
                request,
                db,
                selected_source=source,
                connector=status,
                categories=categories,
                selected_category=selected_category,
                products=products,
                hydrated=hydrated,
                current_category_url=category_url,
            ),
        )
    except SourceDiscoveryError as exc:
        return templates.TemplateResponse(
            "add_products/workspace.html",
            C(request, db, error=str(exc)),
            status_code=400,
        )
