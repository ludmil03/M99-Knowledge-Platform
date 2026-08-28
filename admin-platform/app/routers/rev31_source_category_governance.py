from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import User
from app.services.v073_phase45.source_registry_persistence import (
    ApprovedSourceRecord,
    CanonicalCategoryRecord,
    CategoryProposalRecord,
    ProposalStatus,
    SourceProposalRecord,
)
from app.services.v073_phase45.source_registry_approval_queue import (
    ApprovalPermissionError,
    QueueActor,
    approve_category,
    approve_source,
    pending_category_proposals,
    pending_source_proposals,
    propose_category,
    propose_source,
    reject_source,
)

router = APIRouter(prefix="/rev31-governance", tags=["Revision 31 Governance"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _current_user(request: Request, db: Session) -> User:
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Authentication required")
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user


def _actor(user: User) -> QueueActor:
    return QueueActor(
        user_id=str(user.id),
        display_name=getattr(user, "email", None) or getattr(user, "username", None) or str(user.id),
        is_superadmin=bool(getattr(user, "is_superuser", False)),
    )


@router.get("", response_class=HTMLResponse)
def dashboard(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    return templates.TemplateResponse(
        request=request,
        name="rev31_governance/dashboard.html",
        context={"user": user},
    )


@router.get("/sources", response_class=HTMLResponse)
def sources_page(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    approved = list(db.scalars(select(ApprovedSourceRecord).order_by(ApprovedSourceRecord.name.asc())))
    own_proposals = list(
        db.scalars(
            select(SourceProposalRecord)
            .where(SourceProposalRecord.proposed_by_user_id == str(user.id))
            .order_by(SourceProposalRecord.proposed_at.desc())
        )
    )
    return templates.TemplateResponse(
        request=request,
        name="rev31_governance/sources.html",
        context={"user": user, "approved_sources": approved, "proposals": own_proposals},
    )


@router.post("/sources/propose")
def source_propose(
    request: Request,
    source_kind: str = Form(...),
    name: str = Form(...),
    domain: str = Form(...),
    base_url: str = Form(...),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    propose_source(
        db,
        actor=_actor(user),
        source_kind=source_kind,
        name=name,
        domain=domain,
        base_url=base_url,
    )
    return RedirectResponse("/rev31-governance/sources", status_code=303)


@router.get("/categories", response_class=HTMLResponse)
def categories_page(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    approved = list(db.scalars(select(CanonicalCategoryRecord).order_by(CanonicalCategoryRecord.name.asc())))
    own_proposals = list(
        db.scalars(
            select(CategoryProposalRecord)
            .where(CategoryProposalRecord.proposed_by_user_id == str(user.id))
            .order_by(CategoryProposalRecord.proposed_at.desc())
        )
    )
    return templates.TemplateResponse(
        request=request,
        name="rev31_governance/categories.html",
        context={"user": user, "categories": approved, "proposals": own_proposals},
    )


@router.post("/categories/propose")
def category_propose(
    request: Request,
    name: str = Form(...),
    parent_uuid: Optional[str] = Form(None),
    db: Session = Depends(get_db),
):
    user = _current_user(request, db)
    propose_category(db, actor=_actor(user), name=name, parent_uuid=parent_uuid or None)
    return RedirectResponse("/rev31-governance/categories", status_code=303)


@router.get("/approvals", response_class=HTMLResponse)
def approvals_page(request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    actor = _actor(user)
    if not actor.is_superadmin:
        raise HTTPException(status_code=403, detail="Super Admin required")
    return templates.TemplateResponse(
        request=request,
        name="rev31_governance/approvals.html",
        context={
            "user": user,
            "source_proposals": pending_source_proposals(db, actor=actor),
            "category_proposals": pending_category_proposals(db, actor=actor),
        },
    )


@router.post("/approvals/source/{proposal_uuid}/approve")
def source_approve(proposal_uuid: str, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    try:
        approve_source(db, actor=_actor(user), proposal_uuid=proposal_uuid)
    except ApprovalPermissionError:
        raise HTTPException(status_code=403, detail="Super Admin required")
    return RedirectResponse("/rev31-governance/approvals", status_code=303)


@router.post("/approvals/source/{proposal_uuid}/reject")
def source_reject(proposal_uuid: str, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    try:
        reject_source(db, actor=_actor(user), proposal_uuid=proposal_uuid)
    except ApprovalPermissionError:
        raise HTTPException(status_code=403, detail="Super Admin required")
    return RedirectResponse("/rev31-governance/approvals", status_code=303)


@router.post("/approvals/category/{proposal_uuid}/approve")
def category_approve(proposal_uuid: str, request: Request, db: Session = Depends(get_db)):
    user = _current_user(request, db)
    try:
        approve_category(db, actor=_actor(user), proposal_uuid=proposal_uuid)
    except ApprovalPermissionError:
        raise HTTPException(status_code=403, detail="Super Admin required")
    return RedirectResponse("/rev31-governance/approvals", status_code=303)

