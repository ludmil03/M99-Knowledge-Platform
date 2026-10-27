from pathlib import Path
from urllib.parse import quote

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.services.channel_registry_bridge import available_governed_targets, resolve_governed_target_scope
from app.services.v073_phase45.unified_add_products_m2 import normalize_hydrated, target_rows
from app.services.v073_phase45.m99eu_canary_publish_r5 import prepare_canary, execute_canary
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
        "targets": available_governed_targets(),
        "selection_review": None,
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

@router.post("/selection", response_class=HTMLResponse)
def unified_selection_review(request: Request, source_uuid: str = Form(...), selection_mode: str = Form("MULTIPLE_PRODUCTS"), selected_url: list[str] = Form(default=[]), requested_target: list[str] = Form(default=[]), category_url: str = Form(""), db: Session = Depends(get_db)):
    try:
        source, status, categories = _selected_source_context(db, source_uuid)
        mode, clean = validate_selection(selection_mode, selected_url, source)
        scope = resolve_governed_target_scope(requested_target)
        review = {"mode":mode,"selected_urls":list(clean),**scope,"write_performed":False,"publish_enabled":False}
        selected_category = _find_category(categories, category_url) if category_url else None
        products = list_category_products(source, category_url) if category_url else []
        return templates.TemplateResponse("add_products/workspace.html", C(request, db, selected_source=source, connector=status, categories=categories, selected_category=selected_category, products=products, current_category_url=category_url, selection_review=review))
    except (SourceDiscoveryError, ValueError) as exc:
        return templates.TemplateResponse("add_products/workspace.html", C(request, db, error=str(exc)), status_code=400)

# M99_UNIFIED_M2_REVIEW
# M99_M3_REQUESTED_TARGET_SCOPE
@router.post('/m2/review', response_class=HTMLResponse)
def m2_unified_review(request: Request, source_uuid: str = Form(...), product_url: str = Form(...), category_url: str = Form(''), requested_target: list[str] = Form(default=[]), db: Session = Depends(get_db)):
    try:
        scope=resolve_governed_target_scope(requested_target)
        source,status,categories=_selected_source_context(db,source_uuid)
        hydrated=hydrate_product(source,product_url)
        product=normalize_hydrated(hydrated,source.domain)
        # Never prepare a live canary for an unselected target.
        if 'm99.eu' in scope['ready_targets']:
            canary=prepare_canary(product)
        else:
            canary={'ready':False,'blockers':['M99EU_NOT_EXPLICITLY_SELECTED_OR_READY'],'target':'m99.eu'}
        if canary.get('ready'):
            request.session['m99_r5_canary_plan']=canary['plan']
        else:
            request.session.pop('m99_r5_canary_plan',None)
        rows=target_rows(available_governed_targets(),scope['requested_targets'])
        for row in rows:
            if row['key']=='m99.eu' and row['requested'] and not canary.get('ready'):
                row['state']='REQUESTED_BLOCKED'
        return templates.TemplateResponse('add_products/unified_review_m2.html',{'request':request,'product':product,'targets':rows,'publish_enabled':bool(canary.get('ready')),'write_performed':False,'canary':canary,'target_scope':scope})
    except Exception as exc:
        return templates.TemplateResponse('add_products/workspace.html',C(request,db,error='CANARY PREP BLOCKED: '+str(exc)),status_code=400)

# M99_REAL_CANARY_PUBLISH_R5
@router.post('/m99eu-canary/publish', response_class=HTMLResponse)
async def m99eu_canary_publish(request: Request):
    form=await request.form(); plan=request.session.get('m99_r5_canary_plan')
    if not isinstance(plan,dict):
        return HTMLResponse('PUBLISH BLOCKED: NO_SERVER_SIDE_CANARY_PLAN',status_code=400)
    try:
        result=execute_canary(plan,token=str(form.get('scope_token') or ''),operation=str(form.get('operation') or ''),reference=str(form.get('reference') or ''),target=str(form.get('target') or ''),confirmed=str(form.get('operator_confirmed') or '')=='YES')
        request.session.pop('m99_r5_canary_plan',None)
        return HTMLResponse('<h1>REAL M99 CANARY PUBLISH PASS</h1><p>PUBLISHED_READBACK_OK</p><p>Reference: '+str(result.get('reference'))+'</p><p>Remote ID: '+str(result.get('remote_id'))+'</p><p><a href="/add-products">Back to Add Products</a></p>')
    except Exception as exc:
        return HTMLResponse('<h1>PUBLISH BLOCKED / FAILED</h1><pre>'+str(exc)+'</pre><p>NO AUTOMATIC RETRY.</p><p><a href="/add-products">Back</a></p>',status_code=400)
