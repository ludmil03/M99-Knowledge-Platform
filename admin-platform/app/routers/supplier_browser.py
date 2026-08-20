from __future__ import annotations
import json
from fastapi import APIRouter,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import User,Supplier,Channel,UserChannelAccess,UserPreference,ImportJob,ImportJobItem
from app.services.i18n import ui_for
from app.services.supplier_browser import inspect_supplier_page,SupplierReadError
from app.services.import_jobs import authorized_target_codes,create_draft_job
from app.services.audit_service import log_event

router=APIRouter(prefix="/supplier-browser")
templates=Jinja2Templates(directory="app/templates")

def current_user(request,db):
    uid=request.session.get("user_id")
    return db.get(User,int(uid)) if uid else None

def ctx(request,db,user,**kw):
    code=request.session.get("lang")
    if not code:
        pref=db.get(UserPreference,user.id)
        code=pref.admin_language_code if pref else "BG"
    return {"request":request,"user":user,"ui":ui_for(code),"current_lang":code,**kw}

def allowed_suppliers(db):
    return list(db.scalars(select(Supplier).where(Supplier.active.is_(True),Supplier.browser_enabled.is_(True)).order_by(Supplier.name)))

@router.get("")
def home(request:Request,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    auth=authorized_target_codes(db,user)
    return templates.TemplateResponse("supplier_browser/index.html",ctx(request,db,user,suppliers=allowed_suppliers(db),channels=channels,authorized_codes=auth,result=None,error=None))

@router.post("/inspect")
def inspect(request:Request,supplier_id:int=Form(...),url:str=Form(...),db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    supplier=db.get(Supplier,supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:raise HTTPException(400,"Supplier not available")
    try:
        result=inspect_supplier_page(url,supplier.base_url)
    except SupplierReadError as e:
        channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
        return templates.TemplateResponse("supplier_browser/index.html",ctx(request,db,user,suppliers=allowed_suppliers(db),channels=channels,authorized_codes=authorized_target_codes(db,user),result=None,error=str(e)),status_code=400)
    channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    return templates.TemplateResponse("supplier_browser/index.html",ctx(request,db,user,suppliers=allowed_suppliers(db),channels=channels,authorized_codes=authorized_target_codes(db,user),result=result,error=None,selected_supplier=supplier))

@router.post("/create-job")
async def create_job(request:Request,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    form=await request.form()
    supplier_id=int(form.get("supplier_id"))
    source_type=str(form.get("source_type") or "product")
    source_url=str(form.get("source_url") or "")
    selected_urls=form.getlist("selected_url")
    selected_titles=form.getlist("selected_title")
    selected_refs=form.getlist("selected_ref")
    requested_targets=form.getlist("target")
    items=[]
    for i,u in enumerate(selected_urls):
        items.append({"url":str(u),"title":str(selected_titles[i]) if i<len(selected_titles) else "","supplier_reference":str(selected_refs[i]) if i<len(selected_refs) else ""})
    if not items:raise HTTPException(400,"Select at least one product.")
    job=create_draft_job(db,user=user,supplier_id=supplier_id,source_type=source_type,source_url=source_url,items=items,requested_targets=[str(x) for x in requested_targets])
    log_event(db,user_id=user.id,action="import_job.create_draft",entity_type="import_job",entity_id=job.id,details={"job_code":job.job_code,"items":len(items),"requested_targets":requested_targets})
    return RedirectResponse(f"/supplier-browser/job/{job.id}",303)

@router.get("/job/{job_id}")
def job_detail(request:Request,job_id:int,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    job=db.get(ImportJob,job_id)
    if not job:raise HTTPException(404,"Import Job not found")
    if not user.is_superuser and job.created_by_user_id!=user.id:raise HTTPException(403,"Not authorized")
    items=list(db.scalars(select(ImportJobItem).where(ImportJobItem.import_job_id==job.id).order_by(ImportJobItem.id)))
    return templates.TemplateResponse("supplier_browser/job.html",ctx(request,db,user,job=job,items=items,requested=json.loads(job.requested_targets or "[]"),authorized=json.loads(job.authorized_targets or "[]"),blocked=json.loads(job.blocked_targets or "[]")))
