from __future__ import annotations
from html import escape
from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.core.db import get_db
from app.models.entities import ImportJob, ImportJobItem, Product, User
from app.services.v073_phase46.r4_r1_canonical_payload_bridge import build_canonical_payload_preview
from app.services.v073_phase46.palltex_controlled_publish import R7K_CONFIRMATION, PalltexControlledPublishError, publish_palltex_controlled
router=APIRouter(prefix="/products/publish/m99eu/canonical",tags=["R7K4-real-operator-publish"])
def _user(request,db):
    try: uid=request.session.get("user_id")
    except Exception: uid=None
    if not uid:return None
    try:return db.get(User,int(uid))
    except Exception:return None
def _items(db,job_id):
    rows=db.execute(select(ImportJobItem).where(ImportJobItem.import_job_id==int(job_id)).order_by(ImportJobItem.id)).scalars().all()
    out=[]
    for x in rows:
        p=db.get(Product,x.matched_product_id) if x.matched_product_id else None
        out.append({"id":x.id,"title":x.source_title or "(без име)","supplier_reference":x.supplier_reference or "","m99_reference":getattr(p,"m99_reference","") or ""})
    return out

def _options(items,chosen=""):
    if not items:return '<option value="">Няма продукти в този Job</option>'
    out=[]
    for x in items:
        label=f'#{x["id"]} | {x["m99_reference"] or "M99 pending"} | {x["title"]} | ref {x["supplier_reference"] or "-"}'
        sel=" selected" if str(x["id"])==str(chosen) else ""
        out.append(f'<option value="{_e(x["id"])}"{sel}>{_e(label)}</option>')
    return "".join(out)

def _load(db,job_id,item_id):
    job=db.get(ImportJob,int(job_id));item=db.get(ImportJobItem,int(item_id))
    if job is None:raise ValueError("ImportJob not found.")
    if item is None or int(item.import_job_id)!=int(job.id):raise ValueError("ImportJobItem does not belong to this job.")
    return job,item
def _e(v):return escape("" if v is None else str(v),quote=True)
def _page(job_id=27,item_id="",category_id=26,price_override="",preview=None,result=None,error=None,status=200,items=None):
    items=items or []
    blockers=(preview or {}).get("blockers") or [];ready=bool((preview or {}).get("ready"))
    ident=(preview or {}).get("identifiers") or {};images=(preview or {}).get("images") or {};variants=(preview or {}).get("variants") or {}
    bl="".join("<li>"+_e(x)+"</li>" for x in blockers)
    pv="" if preview is None else f"""<section class=card><h2>Canonical preview: {_e((preview or {}).get('status'))}</h2><p><b>Практически gate:</b> проверката е без измислена цена. Ако evidence е BLOCKED, виждаш точните причини; реалният write остава защитен.</p><p><b>M99 ID:</b> {_e(ident.get('channel_reference'))} | <b>Supplier ref:</b> {_e(ident.get('supplier_reference'))} | <b>Manufacturer MPN:</b> {_e(ident.get('manufacturer_reference'))}</p><p><b>Снимки:</b> {_e(images.get('count'))} | <b>Варианти:</b> {_e(variants.get('rows_count'))}</p>{('<h3>BLOCKERS</h3><ul>'+bl+'</ul>') if blockers else ''}</section>"""
    pub="" if not ready else f"""<section class=danger><h2>READY за реално скрито публикуване</h2><p>Следващият бутон може реално да запише продукт в m99.eu. Резултатът остава hidden / inactive / non-orderable и се проверява с readback.</p><p><b>Цена:</b> реалното HIDDEN публикуване все още изисква положителна цена и READY evidence.</p><form method=post action="/products/publish/m99eu/canonical/publish"><input type=hidden name=job_id value="{_e(job_id)}"><input type=hidden name=item_id value="{_e(item_id)}"><input type=hidden name=category_id value="{_e(category_id)}"><input type=hidden name=price_override value="{_e(price_override)}" placeholder="незадължително за проверката"><label><input type=checkbox name=operator_approved value=yes required> Потвърждавам реалното HIDDEN публикуване</label><br><br><button class=red type=submit>2. ПУБЛИКУВАЙ СКРИТО В m99.eu</button></form></section>"""
    err="" if not error else f"<section class=stop><b>STOP:</b> {_e(error)}</section>"
    res=""
    if result:
        rows="".join(f"<tr><th>{_e(k)}</th><td>{_e(v)}</td></tr>" for k,v in result.items());res=f"<section class=card><h2>API write + readback резултат</h2><table>{rows}</table></section>"
    h=f"""<!doctype html><html lang=bg><head><meta charset=utf-8><title>M99 Knowledge — Реално публикуване</title><style>body{{font-family:Arial;background:#f4f6f8;color:#18202a;margin:0}}main{{max-width:1050px;margin:28px auto;padding:20px}}.card,.danger,.stop,.ok{{background:white;border:1px solid #ccd3da;border-radius:8px;padding:18px;margin:16px 0}}.danger{{border:2px solid #b23b3b}}.stop{{border:2px solid #b00020;background:#fff5f5}}.ok{{background:#eaf7ed}}input{{padding:8px;margin:5px}}button{{padding:10px 16px}}.red{{background:#a51f2b;color:white;border:0}}th,td{{border:1px solid #ddd;padding:8px}}</style></head><body><main><h1>Реално публикуване в m99.eu</h1><p class=ok><b>R7K.4 R7.2.3.2</b> — операторският екран е зареден. HIDDEN-FIRST / READBACK REQUIRED.</p><section class=card><h2>1. Провери продукта</h2><form method=post action="/products/publish/m99eu/canonical/preview"><label>Import Job ID <input name=job_id type=number min=1 required value="{_e(job_id)}"></label><label> Продукт <select name=item_id required>{_options(items,item_id)}</select></label><label> Категория m99.eu <input name=category_id type=number min=1 required value="{_e(category_id)}"></label><label> Пилотна цена <input name=price_override value="{_e(price_override)}" placeholder="незадължително за проверката"></label><button type=submit>1. ПРОВЕРИ ПРОДУКТА</button></form></section>{pv}{pub}{err}{res}</main></body></html>"""
    return HTMLResponse(h,status_code=status,headers={"Cache-Control":"no-store"})
@router.get("",response_class=HTMLResponse)
def page(request:Request,job_id:int=27,db:Session=Depends(get_db)):
    if _user(request,db) is None:return RedirectResponse("/login",303)
    try: items=_items(db,job_id);err=None if items else "В този Import Job няма продукти."
    except Exception as exc:items=[];err=str(exc)
    return _page(job_id=job_id,items=items,error=err)
@router.get("/runtime-check",response_class=HTMLResponse)
def runtime_check():
    return HTMLResponse("<!doctype html><meta charset=utf-8><h1>R7.2.1 RUNTIME PASS</h1><p>No write performed.</p>",headers={"Cache-Control":"no-store"})
@router.post("/preview",response_class=HTMLResponse)
def preview(request:Request,job_id:int=Form(...),item_id:int=Form(...),category_id:int=Form(26),price_override:str=Form(""),db:Session=Depends(get_db)):
    if _user(request,db) is None:return RedirectResponse("/login",303)
    try:
        items=_items(db,job_id);job,item=_load(db,job_id,item_id);p=build_canonical_payload_preview(job=job,item=item);err=None if p.get("ready") else "Продуктът е BLOCKED. Реално публикуване не е разрешено."
    except Exception as exc:p=None;err=str(exc)
    return _page(job_id,item_id,category_id,price_override,p,None,err,items=items)
@router.post("/publish",response_class=HTMLResponse)
def publish(request:Request,job_id:int=Form(...),item_id:int=Form(...),category_id:int=Form(...),price_override:str=Form(...),operator_approved:str=Form(""),db:Session=Depends(get_db)):
    user=_user(request,db)
    if user is None:return RedirectResponse("/login",303)
    items=_items(db,job_id)
    if not bool(getattr(user,"is_superuser",False)):return _page(job_id,item_id,category_id,price_override,error="Само Super Admin може да публикува.",status=403,items=items)
    if operator_approved!="yes":return _page(job_id,item_id,category_id,price_override,error="Операторското потвърждение е задължително.",status=400,items=items)
    try:
        job,item=_load(db,job_id,item_id);p=build_canonical_payload_preview(job=job,item=item)
        if not p.get("ready"):raise PalltexControlledPublishError("Canonical preview is BLOCKED: "+"; ".join(p.get("blockers") or []))
        r=publish_palltex_controlled(db,user=user,job=job,item=item,preview=p,category_id=int(category_id),price_override=price_override,confirmation=R7K_CONFIRMATION)
        out={"created":bool(r.created),"product_id":r.product_id,"reference":r.reference,"active":r.active,"available_for_order":r.available_for_order,"visibility":r.visibility,"price":r.price,"api_truth_verified":bool(r.api_truth_verified),"truth_summary":r.truth_summary,"correlation_id":r.correlation_id}
        return _page(job_id,item_id,category_id,price_override,p,out,None if r.api_truth_verified else "API truth verification failed.",200 if r.api_truth_verified else 409,items=items)
    except Exception as exc:return _page(job_id,item_id,category_id,price_override,error=str(exc),status=409,items=items)
