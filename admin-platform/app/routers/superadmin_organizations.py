import os
from pathlib import Path
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.services.v073_phase4.superadmin_organizations import list_organizations, decide_organization, configure_supplier_source
router=APIRouter(prefix="/superadmin/organizations",tags=["superadmin-organizations"])
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parents[1]/"templates"))
def db(): 
    v=os.getenv("M99_ADMIN_DATABASE_URL","").strip()
    if not v: raise RuntimeError("M99_ADMIN_DATABASE_URL is required")
    return v
def superadmin(r):
    try: return str(r.session.get("role") or r.session.get("user_role") or "").upper() in {"SUPER_ADMIN","SUPERADMIN"}
    except: return False
@router.get("",response_class=HTMLResponse)
def home(request:Request):
    if not superadmin(request): return RedirectResponse("/login",303)
    return templates.TemplateResponse(request=request,name="superadmin_organizations/index.html",
        context={"title":"Organizations","organizations":list_organizations(db())})
@router.post("/{organization_id}/decision")
def decision(request:Request,organization_id:str,action:str=Form(...),reason:str=Form(""),merge_target_organization_id:str=Form("")):
    if not superadmin(request): return RedirectResponse("/login",303)
    actor=str(request.session.get("username") or request.session.get("user_id") or "superadmin")
    decide_organization(db(),organization_id=organization_id,action=action,actor=actor,reason=reason or None,
        merge_target_organization_id=merge_target_organization_id or None)
    return RedirectResponse("/superadmin/organizations",303)
@router.post("/{organization_id}/sources/{source_id}/configure")
def cfg(request:Request,organization_id:str,source_id:str,status:str=Form(...),operator_browsable:str|None=Form(None)):
    if not superadmin(request): return RedirectResponse("/login",303)
    actor=str(request.session.get("username") or request.session.get("user_id") or "superadmin")
    configure_supplier_source(db(),organization_id=organization_id,source_id=source_id,actor=actor,status=status,
        operator_browsable=(operator_browsable=="on"),read_only=True)
    return RedirectResponse("/superadmin/organizations",303)
