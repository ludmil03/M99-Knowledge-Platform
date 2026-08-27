from __future__ import annotations
import json
from fastapi import APIRouter, Request, Depends, Form, HTTPException
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import (
    User, Supplier, Channel, UserPreference, ImportJob, ImportJobItem
)
from app.services.i18n import ui_for
from app.services.supplier_browser import (
    inspect_supplier_page, hydrate_stenso_product, SupplierReadError
)
from app.services.manufacturer_enrichment import (
    hydrate_manufacturer_product, compare_identity, merged_evidence, ManufacturerReadError
)
from app.services.import_jobs import authorized_target_codes, create_draft_job
from app.services.audit_service import log_event
from app.services.source_role_guard import validate_manufacturer_source
from app.services.canonical_preview import prepare_canonical_preview

router = APIRouter(prefix="/supplier-browser")
templates = Jinja2Templates(directory="app/templates")

def current_user(request, db):
    uid = request.session.get("user_id")
    return db.get(User, int(uid)) if uid else None

def ctx(request, db, user, **kw):
    code = request.session.get("lang")
    if not code:
        pref = db.get(UserPreference, user.id)
        code = pref.admin_language_code if pref else "BG"
    return {
        "request": request,
        "user": user,
        "ui": ui_for(code),
        "current_lang": code,
        **kw,
    }

def allowed_suppliers(db):
    return list(db.scalars(
        select(Supplier).where(
            Supplier.active.is_(True),
            Supplier.browser_enabled.is_(True),
        ).order_by(Supplier.name)
    ))

def channels_context(db, user):
    channels = list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    return channels, authorized_target_codes(db, user)

@router.get("")
def home(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    channels, auth = channels_context(db, user)
    return templates.TemplateResponse(
        "supplier_browser/index.html",
        ctx(
            request, db, user,
            suppliers=allowed_suppliers(db),
            channels=channels,
            authorized_codes=auth,
            result=None,
            error=None,
        ),
    )

@router.post("/inspect")
def inspect(
    request: Request,
    supplier_id: int = Form(...),
    url: str = Form(...),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        raise HTTPException(400, "Supplier not available")

    try:
        result = inspect_supplier_page(url, supplier.base_url)
    except SupplierReadError as exc:
        channels, auth = channels_context(db, user)
        return templates.TemplateResponse(
            "supplier_browser/index.html",
            ctx(
                request, db, user,
                suppliers=allowed_suppliers(db),
                channels=channels,
                authorized_codes=auth,
                result=None,
                error=str(exc),
            ),
            status_code=400,
        )

    channels, auth = channels_context(db, user)
    return templates.TemplateResponse(
        "supplier_browser/index.html",
        ctx(
            request, db, user,
            suppliers=allowed_suppliers(db),
            channels=channels,
            authorized_codes=auth,
            result=result,
            error=None,
            selected_supplier=supplier,
        ),
    )


@router.get("/hydrate-product")
def hydrate_product_runtime(
    request: Request,
    supplier_id: int,
    url: str,
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return JSONResponse({"status":"FAIL","error":"AUTH_REQUIRED"}, status_code=401)

    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        return JSONResponse({"status":"FAIL","error":"SUPPLIER_NOT_AVAILABLE"}, status_code=400)

    try:
        if "stenso.net" not in (supplier.base_url or "").lower():
            return JSONResponse({"status":"FAIL","error":"RUNTIME_HYDRATION_NOT_IMPLEMENTED"}, status_code=400)
        product = hydrate_stenso_product(url, supplier.base_url, use_cache=True)
        return JSONResponse({
            "status": product.get("hydration_status","FAIL"),
            "product": product,
        })
    except Exception as exc:
        return JSONResponse({"status":"FAIL","error":str(exc)}, status_code=409)

@router.post("/create-job")
async def create_job(request: Request, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)

    form = await request.form()
    supplier_id = int(form.get("supplier_id"))
    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        raise HTTPException(400, "Supplier not available")

    source_type = str(form.get("source_type") or "product")
    source_url = str(form.get("source_url") or "")
    selected_urls = [str(x) for x in form.getlist("selected_url")]
    requested_targets = [str(x) for x in form.getlist("target")]

    if not selected_urls:
        raise HTTPException(400, "Select at least one product.")

    # SECURITY / DATA-INTEGRITY:
    # Never trust hidden title/ref values from the browser. Re-read only the
    # selected supplier URLs and use supplier-verified identity fields.
    items = []
    read_errors = []
    for selected_url in selected_urls:
        try:
            if "stenso.net" in (supplier.base_url or "").lower():
                detail = hydrate_stenso_product(selected_url, supplier.base_url)
                items.append({
                    "url": detail["url"],
                    "title": detail["title"],
                    "supplier_reference": detail["supplier_reference"],
                })
            else:
                check = inspect_supplier_page(selected_url, supplier.base_url)
                product = check["products"][0] if check.get("products") else {}
                items.append({
                    "url": selected_url,
                    "title": product.get("title") or check.get("title") or "",
                    "supplier_reference": product.get("supplier_reference") or "",
                })
        except Exception as exc:
            read_errors.append(f"{selected_url}: {exc}")

    if read_errors:
        raise HTTPException(
            409,
            "Selected product verification failed. DRAFT Import Job was not created. "
            + " | ".join(read_errors[:5]),
        )
    if len(items) != len(selected_urls):
        raise HTTPException(409, "Not all selected products could be verified.")

    job = create_draft_job(
        db,
        user=user,
        supplier_id=supplier_id,
        source_type=source_type,
        source_url=source_url,
        items=items,
        requested_targets=requested_targets,
    )
    log_event(
        db,
        user_id=user.id,
        action="import_job.create_draft",
        entity_type="import_job",
        entity_id=job.id,
        details={
            "job_code": job.job_code,
            "items": len(items),
            "requested_targets": requested_targets,
            "supplier_reverified": True,
        },
    )
    return RedirectResponse(f"/supplier-browser/job/{job.id}", 303)







@router.get("/manufacturer-start")
def manufacturer_start(
    request: Request,
    supplier_id: int,
    supplier_url: str,
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)

    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        raise HTTPException(400, "Supplier not available")

    try:
        if "stenso.net" in (supplier.base_url or "").lower():
            supplier_product = hydrate_stenso_product(supplier_url, supplier.base_url)
        else:
            inspected = inspect_supplier_page(supplier_url, supplier.base_url)
            supplier_product = inspected["products"][0] if inspected.get("products") else {
                "url": supplier_url,
                "title": inspected.get("title") or "",
                "supplier_reference": "",
                "price_text": "",
                "availability_text": "UNKNOWN",
                "images": [],
            }
    except Exception as exc:
        raise HTTPException(409, f"Supplier re-read failed: {exc}")

    return templates.TemplateResponse(
        "supplier_browser/manufacturer_start.html",
        ctx(
            request, db, user,
            supplier=supplier,
            supplier_product=supplier_product,
        ),
    )

@router.post("/manufacturer-review")
def manufacturer_review(
    request: Request,
    supplier_id: int = Form(...),
    supplier_url: str = Form(...),
    manufacturer_url: str = Form(...),
    db: Session = Depends(get_db),
):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)

    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        raise HTTPException(400, "Supplier not available")

    ok, reason = validate_manufacturer_source(supplier.base_url, manufacturer_url)
    if not ok:
        raise HTTPException(
            400,
            "Manufacturer source invalid: "
            + reason
            + ". STENSO is the supplier source; enter the official manufacturer product URL."
        )

    try:
        supplier_product = hydrate_stenso_product(supplier_url, supplier.base_url)
        manufacturer_product = hydrate_manufacturer_product(manufacturer_url)
        identity = compare_identity(supplier_product, manufacturer_product)
        evidence = merged_evidence(supplier_product, manufacturer_product)
    except (SupplierReadError, ManufacturerReadError) as exc:
        raise HTTPException(409, f"Multi-source hydration failed: {exc}")

    channels, auth = channels_context(db, user)
    return templates.TemplateResponse(
        "supplier_browser/manufacturer_review.html",
        ctx(
            request, db, user,
            supplier=supplier,
            supplier_product=supplier_product,
            manufacturer_product=manufacturer_product,
            identity=identity,
            evidence=evidence,
            channels=channels,
            authorized_codes=auth,
        ),
    )

@router.get("/job/{job_id}")
def job_detail(request: Request, job_id: int, db: Session = Depends(get_db)):
    user = current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    job = db.get(ImportJob, job_id)
    if not job:
        raise HTTPException(404, "Import Job not found")
    if not user.is_superuser and job.created_by_user_id != user.id:
        raise HTTPException(403, "Not authorized")
    items = list(db.scalars(
        select(ImportJobItem).where(
            ImportJobItem.import_job_id == job.id
        ).order_by(ImportJobItem.id)
    ))
    return templates.TemplateResponse(
        "supplier_browser/job.html",
        ctx(
            request, db, user,
            job=job,
            items=items,
            requested=json.loads(job.requested_targets or "[]"),
            authorized=json.loads(job.authorized_targets or "[]"),
            blocked=json.loads(job.blocked_targets or "[]"),
        ),
    )
