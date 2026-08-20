from __future__ import annotations
import json
from fastapi import APIRouter,Request,Depends,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select,desc
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import User,UserPreference,ImportJob
from app.models.preflight import ImportPreflight
from app.services.i18n import ui_for
from app.services.preflight import run_preflight
from app.services.audit_service import log_event

router=APIRouter(prefix='/preflight')
templates=Jinja2Templates(directory='app/templates')

def current_user(request,db):
    uid=request.session.get('user_id');return db.get(User,int(uid)) if uid else None

def ctx(request,db,user,**kw):
    code=request.session.get('lang')
    if not code:
        pref=db.get(UserPreference,user.id);code=pref.admin_language_code if pref else 'BG'
    return {'request':request,'user':user,'ui':ui_for(code),'current_lang':code,**kw}

@router.post('/job/{job_id}/run')
def run_job_preflight(request:Request,job_id:int,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse('/login',303)
    job=db.get(ImportJob,job_id)
    if not job:raise HTTPException(404,'Import Job not found')
    if not user.is_superuser and job.created_by_user_id!=user.id:raise HTTPException(403,'Not authorized')
    pf=run_preflight(db,job)
    log_event(db,user_id=user.id,action='import_job.preflight',entity_type='import_job',entity_id=job.id,details={'preflight_id':pf.id,'status':pf.status})
    return RedirectResponse(f'/preflight/job/{job.id}',303)

@router.get('/job/{job_id}')
def view_preflight(request:Request,job_id:int,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse('/login',303)
    job=db.get(ImportJob,job_id)
    if not job:raise HTTPException(404,'Import Job not found')
    if not user.is_superuser and job.created_by_user_id!=user.id:raise HTTPException(403,'Not authorized')
    pf=db.scalar(select(ImportPreflight).where(ImportPreflight.import_job_id==job.id).order_by(desc(ImportPreflight.id)))
    report=json.loads(pf.report_json or '{}') if pf else {}
    findings=json.loads(pf.findings_json or '[]') if pf else []
    ready=json.loads(pf.ready_targets_json or '[]') if pf else []
    blocked=json.loads(pf.blocked_targets_json or '[]') if pf else []
    return templates.TemplateResponse('preflight/job.html',ctx(request,db,user,job=job,pf=pf,report=report,findings=findings,ready=ready,blocked=blocked))
