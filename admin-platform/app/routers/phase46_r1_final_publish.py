from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import ImportJob, User, UserPreference
from app.services.i18n import ui_for
from app.services.v073_phase45.m99eu_r37_auto_publish import (
    AutoPublishError,
    DEFAULT_CATEGORY_ID,
    R1_CONFIRMATION,
    eligible_draft_jobs,
    publish_existing_draft_job,
    supplier_product_from_draft_item,
)
from app.models.entities import ImportJobItem
from app.services.v073_phase46.canonical_identity_allocator import CanonicalIdentityAllocationError, allocate_or_reuse_for_item
from app.services.v073_phase46.r4_r1_canonical_payload_bridge import build_canonical_payload_preview
from app.services.v073_phase46.canonical_live_pilot import CanonicalPilotError, CONFIRMATION as R7D_CONFIRMATION, publish_canonical_pilot
from app.services.v073_phase46.palltex_controlled_publish import (
    PalltexControlledPublishError, R7K_CONFIRMATION, publish_palltex_controlled,
)
from app.services.v073_phase46.secure_integration_settings import (
    SecureSettingsError, effective_m99eu_credentials, public_m99eu_status, save_m99eu_settings, verify_m99eu_connection, back_office_product_url,
)

router = APIRouter(prefix="/r1-final", tags=["Phase 4.6 R1 FINAL"])
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


def _job_snapshot(db: Session, job: ImportJob):
    items = (
        db.query(ImportJobItem)
        .filter(ImportJobItem.import_job_id == int(job.id))
        .order_by(ImportJobItem.id.asc())
        .all()
    )
    selected = [x for x in items if bool(getattr(x, "selected", False))]
    product = supplier_product_from_draft_item(selected[0]) if len(selected) == 1 else {}
    return items, selected, product


@router.get("", response_class=HTMLResponse)
def control_page(
    request: Request,
    job_id: int | None = None,
    integration_saved: int | None = None,
    integration_test: str | None = None,
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    if not user.is_superuser:
        raise HTTPException(403, "Phase 4.6 R1 FINAL first live product is Super Admin only.")

    jobs = eligible_draft_jobs(db, limit=50)
    selected_job = db.get(ImportJob, int(job_id)) if job_id else None
    if selected_job is not None and str(selected_job.status).upper() != "DRAFT":
        raise HTTPException(409, "Selected ImportJob is not DRAFT.")

    items = []
    selected_items = []
    product = {}
    payload_preview = {}
    if selected_job is not None:
        items, selected_items, product = _job_snapshot(db, selected_job)
        if len(selected_items) == 1:
            try:
                payload_preview = build_canonical_payload_preview(job=selected_job, item=selected_items[0])
            except Exception as exc:
                payload_preview = {"status":"BLOCKED","ready":False,"write_allowed":False,"blockers":[f"Preview failed safely: {exc}"],"warnings":[]}

    return templates.TemplateResponse(
        "operator_publish/phase46_r1_final.html",
        _ctx(
            request,
            db,
            user,
            jobs=jobs,
            selected_job=selected_job,
            items=items,
            selected_items=selected_items,
            product=product,
            default_category_id=DEFAULT_CATEGORY_ID,
            confirmation=R7D_CONFIRMATION,
            r7k_confirmation=R7K_CONFIRMATION,
            payload_preview=payload_preview,
            integration_status=public_m99eu_status(),
            integration_saved=bool(integration_saved),
            integration_test=integration_test or "",
        ),
    )




@router.post("/complete-identity")
def complete_identity(
    request: Request,
    job_id: int = Form(...),
    confirmation: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    if not user.is_superuser:
        raise HTTPException(403, "Canonical identity completion is Super Admin only.")
    if str(confirmation or "").strip() != "CREATE PERMANENT M99 ID":
        raise HTTPException(409, "Exact canonical identity confirmation text is required.")

    job=db.get(ImportJob,int(job_id))
    if not job:
        raise HTTPException(404,"ImportJob not found.")
    if str(getattr(job,"status","")).upper()!="DRAFT":
        raise HTTPException(409,"Canonical identity may be completed only for a DRAFT ImportJob.")

    items, selected_items, _product = _job_snapshot(db,job)
    if len(selected_items)!=1:
        raise HTTPException(409,f"Exactly one selected DRAFT item is required; found {len(selected_items)}.")
    try:
        result=allocate_or_reuse_for_item(db,item=selected_items[0])
    except CanonicalIdentityAllocationError as exc:
        raise HTTPException(409,str(exc))
    return RedirectResponse(
        url=f"/operator-publish/r1-final?job_id={int(job.id)}&identity_completed=1",
        status_code=303,
    )


@router.post("/integration-settings/save")
def save_integration_settings(request:Request,job_id:int|None=Form(None),api_key:str=Form(""),enabled:str|None=Form(None),back_office_url:str=Form(""),db:Session=Depends(get_db)):
    user=_current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    if not user.is_superuser:raise HTTPException(403,"Integration Settings are Super Admin only.")
    try:save_m99eu_settings(api_key=api_key,enabled=(enabled=="1"),back_office_url=back_office_url)
    except SecureSettingsError as exc:raise HTTPException(409,str(exc))
    q="?integration_saved=1"+(f"&job_id={int(job_id)}" if job_id else "")
    return RedirectResponse("/operator-publish/r1-final"+q,303)

@router.post("/integration-settings/verify")
def verify_integration_settings(request:Request,job_id:int|None=Form(None),db:Session=Depends(get_db)):
    user=_current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    if not user.is_superuser:raise HTTPException(403,"Integration Settings are Super Admin only.")
    try:
        enabled,key,source=effective_m99eu_credentials();verify_m99eu_connection(key);result="ok"
    except Exception:result="fail"
    q=f"?integration_test={result}"+(f"&job_id={int(job_id)}" if job_id else "")
    return RedirectResponse("/operator-publish/r1-final"+q,303)


@router.get("/truth-verify", response_class=HTMLResponse)
def truth_verify(
    request:Request,
    product_id:int,
    reference:str,
    category_id:int|None=None,
    price:str|None=None,
    known_good_product_id:int|None=None,
    db:Session=Depends(get_db),
):
    user=_current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    if not user.is_superuser:raise HTTPException(403,"Product truth verification is Super Admin only.")
    try:
        enabled,key,source=effective_m99eu_credentials()
        if not key:raise CanonicalPilotError("m99.eu API key is not configured.")
        from app.services.v073_phase46.live_product_truth_verifier import verify_product_truth
        truth=verify_product_truth(
            key,product_id=product_id,reference=reference,expected_category_id=category_id,expected_price=price,
            require_hidden=True,known_good_product_id=known_good_product_id
        )
        error=None
    except Exception as exc:
        truth=None;error=str(exc)
    return templates.TemplateResponse(
        "operator_publish/phase46_r7g_truth_result.html",
        _ctx(request,db,user,truth=truth,truth_error=error,back_office_url=back_office_product_url(product_id)),
        status_code=409 if error else 200,
    )

@router.post("/publish-palltex", response_class=HTMLResponse)
def publish_palltex_one(
    request: Request,
    job_id: int = Form(...),
    category_id: int = Form(DEFAULT_CATEGORY_ID),
    confirmation: str = Form(""),
    price_override: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    if not user.is_superuser:
        raise HTTPException(403, "R7K Palltex controlled publish is Super Admin only.")

    job = db.get(ImportJob, int(job_id))
    if not job:
        raise HTTPException(404, "ImportJob not found.")
    items, selected_items, product = _job_snapshot(db, job)
    try:
        if len(selected_items) != 1:
            raise PalltexControlledPublishError(
                f"R7K requires exactly one selected item; found {len(selected_items)}."
            )
        payload_preview = build_canonical_payload_preview(job=job, item=selected_items[0])
        result = publish_palltex_controlled(
            db, user=user, job=job, item=selected_items[0], preview=payload_preview,
            category_id=category_id, price_override=price_override, confirmation=confirmation,
        )
        error = None
    except (PalltexControlledPublishError, CanonicalPilotError, AutoPublishError) as exc:
        result = None
        error = str(exc)

    return templates.TemplateResponse(
        "operator_publish/phase46_r7d_live_result.html",
        _ctx(
            request, db, user, job=job, items=items, selected_items=selected_items, product=product,
            publish_result=result, publish_error=error,
            back_office_url=back_office_product_url(result.product_id) if result else "",
        ),
        status_code=409 if error else 200,
    )


@router.post("/publish", response_class=HTMLResponse)
def publish_one(
    request: Request,
    job_id: int = Form(...),
    category_id: int = Form(DEFAULT_CATEGORY_ID),
    confirmation: str = Form(""),
    price_override: str = Form(""),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)
    if not user.is_superuser:
        raise HTTPException(403, "Phase 4.6 R1 FINAL first live product is Super Admin only.")

    job = db.get(ImportJob, int(job_id))
    if not job:
        raise HTTPException(404, "ImportJob not found.")
    items, selected_items, product = _job_snapshot(db, job)
    try:
        if len(selected_items) != 1:
            raise CanonicalPilotError(f"R7D requires exactly one selected item; found {len(selected_items)}.")
        payload_preview = build_canonical_payload_preview(job=job, item=selected_items[0])
        result = publish_canonical_pilot(
            db, user=user, job=job, item=selected_items[0], preview=payload_preview,
            category_id=category_id, price_override=price_override, confirmation=confirmation,
        )
        error = None
    except (CanonicalPilotError, AutoPublishError) as exc:
        result = None
        error = str(exc)

    return templates.TemplateResponse(
        "operator_publish/phase46_r7d_live_result.html",
        _ctx(
            request,
            db,
            user,
            job=job,
            items=items,
            selected_items=selected_items,
            product=product,
            publish_result=result,
            publish_error=error,
            back_office_url=back_office_product_url(result.product_id) if result else "",
        ),
        status_code=409 if error else 200,
    )
