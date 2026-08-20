from fastapi import APIRouter,Request,Form,Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.services.auth_service import authenticate
from app.services.audit_service import log_event

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

@router.get("/login")
def login_page(request:Request):
    if request.session.get("user_id"):return RedirectResponse("/",status_code=303)
    return templates.TemplateResponse("auth/login.html",{"request":request,"error":None})

@router.post("/login")
def login(request:Request,login:str=Form(...),password:str=Form(...),db:Session=Depends(get_db)):
    user=authenticate(db,login,password);ip=request.client.host if request.client else ""
    if not user:
        log_event(db,action="auth.login",result="DENIED",details={"login":login},ip_address=ip)
        return templates.TemplateResponse("auth/login.html",{"request":request,"error":"Невалидно потребителско име/имейл или парола."},status_code=401)
    request.session.clear();request.session["user_id"]=user.id
    log_event(db,user_id=user.id,action="auth.login",result="OK",ip_address=ip)
    return RedirectResponse("/",status_code=303)

@router.post("/logout")
def logout(request:Request,db:Session=Depends(get_db)):
    uid=request.session.get("user_id");ip=request.client.host if request.client else ""
    if uid:log_event(db,user_id=int(uid),action="auth.logout",ip_address=ip)
    request.session.clear()
    return RedirectResponse("/login",status_code=303)
