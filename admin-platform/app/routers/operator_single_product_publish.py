from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import ImportJobItem
from app.services.v073_phase45.m99eu_operator_single_publish import (
    DEFAULT_CATEGORY_ID,
    PublishSafetyError,
    append_audit,
    candidate_from_item,
    publish_one,
)

router = APIRouter(prefix="/operator-publish", tags=["operator-single-product-publish"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _user_label(request: Request) -> str:
    user = request.session.get("user_id") if hasattr(request, "session") else None
    return f"user_id:{user}" if user is not None else "operator"


@router.get("/m99eu", response_class=HTMLResponse)
def choose_product(request: Request, db: Session = Depends(get_db)):
    rows = db.query(ImportJobItem).order_by(ImportJobItem.id.desc()).limit(100).all()
    candidates = [candidate_from_item(r) for r in rows]
    return templates.TemplateResponse(
        "operator_publish/m99eu_single.html",
        {
            "request": request,
            "candidates": candidates,
            "default_category_id": DEFAULT_CATEGORY_ID,
            "result": None,
            "error": None,
        },
    )


@router.post("/m99eu", response_class=HTMLResponse)
def publish_product(
    request: Request,
    item_id: int = Form(...),
    category_id: int = Form(DEFAULT_CATEGORY_ID),
    api_key: str = Form(...),
    confirmation: str = Form(...),
    db: Session = Depends(get_db),
):
    row = db.query(ImportJobItem).filter(ImportJobItem.id == item_id).first()
    if row is None:
        raise HTTPException(status_code=404, detail="ImportJobItem not found")

    candidate = candidate_from_item(row)
    try:
        result = publish_one(candidate, api_key, category_id, confirmation)
        repo_root = Path(__file__).resolve().parents[3]
        audit_path = append_audit(repo_root, _user_label(request), candidate, result)
        rows = db.query(ImportJobItem).order_by(ImportJobItem.id.desc()).limit(100).all()
        candidates = [candidate_from_item(r) for r in rows]
        return templates.TemplateResponse(
            "operator_publish/m99eu_single.html",
            {
                "request": request,
                "candidates": candidates,
                "default_category_id": category_id,
                "result": {
                    "created": result.created,
                    "product_id": result.product_id,
                    "reference": result.reference,
                    "active": result.active,
                    "category_id": result.category_id,
                    "correlation_id": result.correlation_id,
                    "audit_path": str(audit_path),
                },
                "error": None,
            },
        )
    except PublishSafetyError as exc:
        rows = db.query(ImportJobItem).order_by(ImportJobItem.id.desc()).limit(100).all()
        candidates = [candidate_from_item(r) for r in rows]
        return templates.TemplateResponse(
            "operator_publish/m99eu_single.html",
            {
                "request": request,
                "candidates": candidates,
                "default_category_id": category_id,
                "result": None,
                "error": str(exc),
            },
            status_code=400,
        )

# M99_PHASE46_R1_FINAL_INCLUDE
from app.routers.phase46_r1_final_publish import router as phase46_r1_final_router
from app.routers.phase46_r3_content_intelligence import router as phase46_r3_content_router
router.include_router(phase46_r1_final_router)
router.include_router(phase46_r3_content_router)
