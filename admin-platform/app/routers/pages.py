from fastapi import APIRouter,Request,Depends
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select,func,desc
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import User,Product,ProductPresence,Supplier,ImportJob,AuditLog,Channel,UserPreference
from app.services.i18n import ui_for
router=APIRouter();templates=Jinja2Templates(directory="app/templates")
def get_user(request,db):
    uid=request.session.get("user_id");return db.get(User,int(uid)) if uid else None
def ctx(request,db,user,**kwargs):
    code=request.session.get("lang")
    if not code:
        pref=db.get(UserPreference,user.id);code=pref.admin_language_code if pref else "BG"
    return {"request":request,"user":user,"ui":ui_for(code),"current_lang":code,**kwargs}
@router.get("/")
def dashboard(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    metrics={"products":db.scalar(select(func.count(Product.id))) or 0,"suppliers":db.scalar(select(func.count(Supplier.id))) or 0,"channels":db.scalar(select(func.count(Channel.id))) or 0,"import_jobs":db.scalar(select(func.count(ImportJob.id))) or 0}
    jobs=list(db.scalars(select(ImportJob).order_by(desc(ImportJob.created_at)).limit(8)))
    return templates.TemplateResponse("dashboard/index.html",ctx(request,db,user,metrics=metrics,latest_jobs=jobs))
@router.get("/products")
def products(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    return templates.TemplateResponse("products/list.html",ctx(request,db,user,products=list(db.scalars(select(Product).order_by(Product.id.desc()).limit(250)))))
@router.get("/presence")
def presence(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    products=list(db.scalars(select(Product).order_by(Product.id.desc()).limit(100)));channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.id)));pres=list(db.scalars(select(ProductPresence)));matrix={(x.product_id,x.channel_id):x for x in pres}
    return templates.TemplateResponse("products/presence.html",ctx(request,db,user,products=products,channels=channels,matrix=matrix))
@router.get("/suppliers")
def suppliers(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    return templates.TemplateResponse("suppliers/list.html",ctx(request,db,user,suppliers=list(db.scalars(select(Supplier).order_by(Supplier.name)))))
@router.get("/imports")
def imports(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    return templates.TemplateResponse("imports/list.html",ctx(request,db,user,jobs=list(db.scalars(select(ImportJob).order_by(desc(ImportJob.created_at)).limit(100)))))
@router.get("/sync")
def sync_page(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    return templates.TemplateResponse("sync/index.html",ctx(request,db,user))
@router.get("/audit")
def audit(request:Request,db:Session=Depends(get_db)):
    user=get_user(request,db)
    if not user:return RedirectResponse("/login",303)
    return templates.TemplateResponse("audit/list.html",ctx(request,db,user,rows=list(db.scalars(select(AuditLog).order_by(desc(AuditLog.created_at)).limit(200)))))
