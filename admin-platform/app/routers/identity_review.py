import os
from pathlib import Path
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.v073_phase4.identity_review import list_identity_review_queue, decide_identity_review
router=APIRouter(prefix="/operator/identity-review",tags=["identity-review"])
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parents[1]/"templates"))
def db():
    v=os.getenv("M99_ADMIN_DATABASE_URL","").strip()
    if not v: raise RuntimeError("M99_ADMIN_DATABASE_URL is required")
    return v
def auth(r):
    try:return bool(r.session.get("user_id") or r.session.get("username"))
    except:return False
@router.get("",response_class=HTMLResponse)
def queue(request:Request):
    if not auth(request): return RedirectResponse("/login",303)
    return templates.TemplateResponse(request=request,name="identity_review/index.html",
        context={"title":"Identity Review","items":list_identity_review_queue(db())})
@router.post("/{resolution_id}/decide")
def decide(request:Request,resolution_id:str,decision:str=Form(...),matched_m99_product_id:str=Form("")):
    if not auth(request): return RedirectResponse("/login",303)
    reviewer=str(request.session.get("username") or request.session.get("user_id"))
    decide_identity_review(db(),resolution_id=resolution_id,reviewer=reviewer,decision=decision,
        matched_m99_product_id=matched_m99_product_id or None)
    return RedirectResponse("/operator/identity-review",303)
