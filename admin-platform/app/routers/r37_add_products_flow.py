from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import ImportJob, User, UserPreference
from app.services.canonical_preview import prepare_canonical_preview
from app.services.i18n import ui_for
from app.services.v073_phase45.r37_import_bridge import (
    prepare_context,
    provision_operational_supplier_for_approved_source,
    product_for_canonical_preview,
    resolve_identity_then_create_draft,
)

router = APIRouter(prefix="/add-products/r37", tags=["R3.7 Add Products Flow"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _current_user(request: Request, db: Session):
    uid = request.session.get("user_id")
    return db.get(User, int(uid)) if uid else None


def _ctx(request: Request, db: Session, user: User, **kw):
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


@router.post("/prepare", response_class=HTMLResponse)
def prepare(
    request: Request,
    source_uuid: str = Form(...),
    product_url: str = Form(...),
    category_url: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    try:
        source, hydrated, bridge, targets = prepare_context(
            db, user=user, source_uuid=source_uuid, product_url=product_url
        )
    except Exception as exc:
        raise HTTPException(409, f"R3.7 PREPARE failed: {exc}")

    return templates.TemplateResponse(
        "add_products/r37_prepare.html",
        _ctx(
            request, db, user,
            source=source,
            hydrated=hydrated,
            bridge=bridge,
            targets=targets,
            category_url=category_url,
        ),
    )


@router.post("/provision-operational-supplier", response_class=HTMLResponse)
def provision_operational_supplier(
    request: Request,
    source_uuid: str = Form(...),
    product_url: str = Form(...),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    if not user.is_superuser:
        raise HTTPException(403, "Super Admin permission is required.")
    try:
        result = provision_operational_supplier_for_approved_source(
            db, user=user, source_uuid=source_uuid
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc))
    except Exception as exc:
        raise HTTPException(409, f"Operational Supplier provisioning failed: {exc}")

    return templates.TemplateResponse(
        "add_products/r37_supplier_provisioned.html",
        _ctx(
            request, db, user,
            result=result,
            source_uuid=source_uuid,
            product_url=product_url,
        ),
    )


@router.post("/create-draft", response_class=HTMLResponse)
def create_draft(
    request: Request,
    source_uuid: str = Form(...),
    product_url: str = Form(...),
    target: str = Form(...),
    manufacturer_name: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)

    try:
        result = resolve_identity_then_create_draft(
            db,
            user=user,
            source_uuid=source_uuid,
            product_url=product_url,
            target=target,
            manufacturer_name=manufacturer_name,
        )
    except PermissionError as exc:
        raise HTTPException(403, str(exc))
    except Exception as exc:
        raise HTTPException(409, f"R3.7 Identity/DRAFT failed: {exc}")

    if not result["created"]:
        return templates.TemplateResponse(
            "add_products/r37_identity_blocked.html",
            _ctx(request, db, user, result=result, target=target),
            status_code=409,
        )

    job = result["job"]
    return RedirectResponse(
        f"/add-products/r37/job-created?job_id={job.id}"
        f"&source_uuid={source_uuid}"
        f"&product_url={product_url}"
        f"&target={target}",
        303,
    )


@router.get("/job-created", response_class=HTMLResponse)
def job_created(
    request: Request,
    job_id: int,
    source_uuid: str,
    product_url: str,
    target: str,
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    job = db.get(ImportJob, job_id)
    if not job:
        raise HTTPException(404, "Import Job not found")
    if not user.is_superuser and job.created_by_user_id != user.id:
        raise HTTPException(403, "Not authorized")

    return templates.TemplateResponse(
        "add_products/r37_job_created.html",
        _ctx(
            request, db, user,
            job=job,
            source_uuid=source_uuid,
            product_url=product_url,
            target=target,
        ),
    )


@router.get("/canonical-preview", response_class=HTMLResponse)
def canonical_preview(
    request: Request,
    job_id: int,
    source_uuid: str,
    product_url: str,
    target: str = "m99eu",
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    job = db.get(ImportJob, job_id)
    if not job:
        raise HTTPException(404, "Import Job not found")
    if not user.is_superuser and job.created_by_user_id != user.id:
        raise HTTPException(403, "Not authorized")

    try:
        supplier_product = product_for_canonical_preview(
            db, source_uuid=source_uuid, product_url=product_url
        )
        preview = prepare_canonical_preview(supplier_product, target_code=target)
    except Exception as exc:
        raise HTTPException(409, f"Canonical Preview failed: {exc}")

    return templates.TemplateResponse(
        "add_products/r37_canonical_preview.html",
        _ctx(
            request, db, user,
            job=job,
            supplier_product=supplier_product,
            preview=preview,
            target=target,
        ),
    )
