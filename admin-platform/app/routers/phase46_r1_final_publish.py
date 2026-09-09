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
from app.services.v073_phase46.r4_r1_canonical_payload_bridge import build_canonical_payload_preview

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
            confirmation=R1_CONFIRMATION,
            payload_preview=payload_preview,
        ),
    )


@router.post("/publish", response_class=HTMLResponse)
def publish_one(
    request: Request,
    job_id: int = Form(...),
    category_id: int = Form(DEFAULT_CATEGORY_ID),
    confirmation: str = Form(""),
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
    raise HTTPException(
        409,
        "LIVE WRITE LOCKED: R4→R1 Canonical Payload Bridge is preview-only until separate payload-adapter acceptance."
    )

    items, selected_items, product = _job_snapshot(db, job)
    try:
        result = publish_existing_draft_job(
            db,
            user=user,
            job=job,
            category_id=category_id,
            confirmation=confirmation,
        )
        error = None
    except AutoPublishError as exc:
        result = None
        error = str(exc)

    return templates.TemplateResponse(
        "operator_publish/phase46_r1_final_result.html",
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
        ),
        status_code=409 if error else 200,
    )
