from fastapi import APIRouter,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.core.security import hash_password
from app.models.entities import User,Role,Permission,Channel,Language,UserPreference,UserChannelAccess,ChannelLanguage
from app.services.audit_service import log_event
from app.services.i18n import ui_for

router=APIRouter(prefix="/admin")
templates=Jinja2Templates(directory="app/templates")

def current_user(request,db):
    uid=request.session.get("user_id")
    return db.get(User,int(uid)) if uid else None

def super_only(request,db):
    user=current_user(request,db)
    if not user:return None
    if not user.is_superuser:raise HTTPException(403,"Super Admin required")
    return user

def lang_code(request,db,user):
    code=request.session.get("lang")
    if code:return code
    pref=db.get(UserPreference,user.id)
    return pref.admin_language_code if pref else "BG"

def ctx(request,db,user,**kw):
    code=lang_code(request,db,user)
    return {"request":request,"user":user,"ui":ui_for(code),"current_lang":code,**kw}

@router.get("/users")
def users_page(request:Request,db:Session=Depends(get_db)):
    user=super_only(request,db)
    if not user:return RedirectResponse("/login",303)
    users=list(db.scalars(select(User).order_by(User.username)))
    roles=list(db.scalars(select(Role).order_by(Role.name)))
    channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    access=list(db.scalars(select(UserChannelAccess)))
    amap={(x.user_id,x.channel_id):x for x in access}
    return templates.TemplateResponse("admin/users.html",ctx(request,db,user,users=users,roles=roles,channels=channels,access_map=amap))

@router.post("/users/create")
def create_user(request:Request,username:str=Form(...),email:str=Form(...),full_name:str=Form(""),password:str=Form(...),role_code:str=Form("CHANNEL_MANAGER"),db:Session=Depends(get_db)):
    actor=super_only(request,db)
    if not actor:return RedirectResponse("/login",303)
    if len(password)<12:raise HTTPException(400,"Password must be at least 12 characters")
    if db.scalar(select(User).where((User.username==username)|(User.email==email.lower()))):raise HTTPException(400,"Username or email already exists")
    role=db.scalar(select(Role).where(Role.code==role_code))
    u=User(username=username.strip(),email=email.strip().lower(),full_name=full_name.strip(),password_hash=hash_password(password),active=True,is_superuser=False)
    if role:u.roles.append(role)
    db.add(u);db.commit();db.refresh(u)
    log_event(db,user_id=actor.id,action="user.create",entity_type="user",entity_id=u.id,details={"username":u.username,"role":role_code})
    return RedirectResponse("/admin/users",303)

@router.post("/users/{user_id}/channel/{channel_id}")
def set_channel_access(request:Request,user_id:int,channel_id:int,can_read:str|None=Form(None),can_import_new:str|None=Form(None),can_update_existing:str|None=Form(None),can_activate:str|None=Form(None),can_run_sync:str|None=Form(None),db:Session=Depends(get_db)):
    actor=super_only(request,db)
    if not actor:return RedirectResponse("/login",303)
    row=db.scalar(select(UserChannelAccess).where(UserChannelAccess.user_id==user_id,UserChannelAccess.channel_id==channel_id))
    if not row:
        row=UserChannelAccess(user_id=user_id,channel_id=channel_id);db.add(row)
    row.can_read=can_read=="on";row.can_import_new=can_import_new=="on";row.can_update_existing=can_update_existing=="on";row.can_activate=can_activate=="on";row.can_run_sync=can_run_sync=="on"
    db.commit()
    log_event(db,user_id=actor.id,action="channel_access.update",entity_type="user",entity_id=user_id,details={"channel_id":channel_id})
    return RedirectResponse("/admin/users",303)

@router.get("/roles")
def roles_page(request:Request,db:Session=Depends(get_db)):
    user=super_only(request,db)
    if not user:return RedirectResponse("/login",303)
    roles=list(db.scalars(select(Role).order_by(Role.name)))
    perms=list(db.scalars(select(Permission).order_by(Permission.code)))
    return templates.TemplateResponse("admin/roles.html",ctx(request,db,user,roles=roles,permissions=perms))

@router.get("/languages")
def languages_page(request:Request,db:Session=Depends(get_db)):
    user=super_only(request,db)
    if not user:return RedirectResponse("/login",303)
    langs=list(db.scalars(select(Language).order_by(Language.sort_order,Language.code)))
    channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    mappings=list(db.scalars(select(ChannelLanguage)))
    mmap={(x.channel_id,x.language_id):x for x in mappings}
    return templates.TemplateResponse("admin/languages.html",ctx(request,db,user,languages=langs,channels=channels,mapping=mmap))

@router.post("/languages/add")
def add_language(request:Request,code:str=Form(...),iso_code:str=Form(""),locale:str=Form(""),name:str=Form(...),native_name:str=Form(...),fallback_code:str=Form("EN"),db:Session=Depends(get_db)):
    actor=super_only(request,db)
    if not actor:return RedirectResponse("/login",303)
    code=code.strip().upper()
    if db.scalar(select(Language).where(Language.code==code)):raise HTTPException(400,"Language code already exists")
    row=Language(code=code,iso_code=iso_code.strip().lower(),locale=locale.strip(),name=name.strip(),native_name=native_name.strip(),fallback_code=fallback_code.strip().upper(),active=True,admin_ui_enabled=False,content_enabled=True,sort_order=100)
    db.add(row);db.commit()
    log_event(db,user_id=actor.id,action="language.add",entity_type="language",entity_id=code)
    return RedirectResponse("/admin/languages",303)

@router.post("/languages/channel/{channel_id}/{language_id}")
def channel_language(request:Request,channel_id:int,language_id:int,active:str|None=Form(None),required:str|None=Form(None),db:Session=Depends(get_db)):
    actor=super_only(request,db)
    if not actor:return RedirectResponse("/login",303)
    row=db.scalar(select(ChannelLanguage).where(ChannelLanguage.channel_id==channel_id,ChannelLanguage.language_id==language_id))
    if not row:row=ChannelLanguage(channel_id=channel_id,language_id=language_id);db.add(row)
    row.active=active=="on";row.required=required=="on";db.commit()
    return RedirectResponse("/admin/languages",303)

@router.post("/language")
def set_language(request:Request,code:str=Form(...),db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse("/login",303)
    lang=db.scalar(select(Language).where(Language.code==code.upper(),Language.active.is_(True),Language.admin_ui_enabled.is_(True)))
    if not lang:raise HTTPException(400,"Admin UI language not enabled")
    request.session["lang"]=lang.code
    pref=db.get(UserPreference,user.id)
    if not pref:pref=UserPreference(user_id=user.id,admin_language_code=lang.code);db.add(pref)
    else:pref.admin_language_code=lang.code
    db.commit()
    return RedirectResponse(request.headers.get("referer") or "/",303)
