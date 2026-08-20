from fastapi import APIRouter,Request,Depends,Form,HTTPException
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import User,UserPreference,Channel
from app.models.preflight import ChannelCommercePolicy
from app.services.i18n import ui_for
from app.services.audit_service import log_event

router=APIRouter(prefix='/admin/commerce')
templates=Jinja2Templates(directory='app/templates')

def current_user(request,db):
    uid=request.session.get('user_id');return db.get(User,int(uid)) if uid else None

def ctx(request,db,user,**kw):
    code=request.session.get('lang')
    if not code:
        pref=db.get(UserPreference,user.id);code=pref.admin_language_code if pref else 'BG'
    return {'request':request,'user':user,'ui':ui_for(code),'current_lang':code,**kw}

@router.get('')
def page(request:Request,db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse('/login',303)
    if not user.is_superuser:raise HTTPException(403,'Super Admin required')
    channels=list(db.scalars(select(Channel).where(Channel.active.is_(True)).order_by(Channel.name)))
    policies={p.channel_id:p for p in db.scalars(select(ChannelCommercePolicy))}
    return templates.TemplateResponse('admin/commerce.html',ctx(request,db,user,channels=channels,policies=policies))

@router.post('/{channel_id}')
def save(request:Request,channel_id:int,country_code:str=Form(''),currency_code:str=Form(''),standard_vat_rate:str=Form(''),publish_price_includes_vat:str|None=Form(None),db:Session=Depends(get_db)):
    user=current_user(request,db)
    if not user:return RedirectResponse('/login',303)
    if not user.is_superuser:raise HTTPException(403,'Super Admin required')
    row=db.get(ChannelCommercePolicy,channel_id)
    if not row:
        row=ChannelCommercePolicy(channel_id=channel_id);db.add(row)
    row.country_code=country_code.strip().upper();row.currency_code=currency_code.strip().upper();row.standard_vat_rate=standard_vat_rate.strip();row.publish_price_includes_vat=publish_price_includes_vat=='on';row.active=True
    db.commit()
    log_event(db,user_id=user.id,action='commerce_policy.update',entity_type='channel',entity_id=channel_id,details={'country':row.country_code,'currency':row.currency_code,'vat':row.standard_vat_rate,'vat_included':row.publish_price_includes_vat})
    return RedirectResponse('/admin/commerce',303)
