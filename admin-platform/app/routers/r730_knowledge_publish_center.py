from __future__ import annotations
import os, json, base64, decimal, secrets
from urllib.request import Request as UrlRequest, urlopen
from urllib.error import HTTPError
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.core.db import SessionLocal
from app.models.entities import ImportJob, ImportJobItem
from app.services.v073_phase46.r4_r1_canonical_payload_bridge import build_canonical_payload_preview

router=APIRouter(prefix="/r730/publish-center",tags=["R7.3 Publish Center"])
templates=Jinja2Templates(directory="app/templates")
CHANNELS=[
 ("m99eu","m99.eu"),("mela99","mela99.com"),("medicinski","medicinski-drehi.com"),
 ("rabotni","rabotni-drehi.com"),("laviro","laviro.ro"),("alviro","alviro.ro"),
 ("toplinka","toplinka.com"),("dolibarr","Dolibarr 20.0.2")]
def _env(n,d=""):
 try:
  import winreg
  with winreg.OpenKey(winreg.HKEY_CURRENT_USER,"Environment") as k:return str(winreg.QueryValueEx(k,n)[0])
 except:return os.getenv(n,d)
def _canonical():
 s=SessionLocal()
 try:
  j=s.get(ImportJob,27); i=s.get(ImportJobItem,29)
  if not j or not i or int(i.import_job_id)!=27:return None,["JOB_ITEM_NOT_FOUND"]
  p=build_canonical_payload_preview(job=j,item=i)
  return p,list(p.get("blockers") or [])
 finally:s.close()
def _ps_get(base,key,pid):
 tok=base64.b64encode((key+":").encode()).decode()
 req=UrlRequest(base.rstrip("/")+"/api/products/"+str(pid)+"?output_format=JSON",
  headers={"Authorization":"Basic "+tok,"Accept":"application/json","User-Agent":"M99-Knowledge-R730"},method="GET")
 try:
  with urlopen(req,timeout=25) as r:return r.status,json.loads(r.read().decode("utf-8","replace"))
 except HTTPError as e:return e.code,{}
 except:return None,{}
def _state(message=""):
 p,block=_canonical(); ids=(p or {}).get("identifiers") or {}
 return {"channels":CHANNELS,"payload":p or {},"blockers":block,"message":message,
  "reference":ids.get("channel_reference",""),"supplier_reference":ids.get("supplier_reference",""),
  "manufacturer_reference":ids.get("manufacturer_reference",""),
  "images":((p or {}).get("images") or {}).get("count",0),
  "variants":((p or {}).get("variants") or {}).get("rows_count",0)}
@router.get("",response_class=HTMLResponse)
def screen(request:Request):
 st=_state();return templates.TemplateResponse("r730_knowledge_publish_center.html",{"request":request,**st})
@router.post("/preflight",response_class=HTMLResponse)
async def preflight(request:Request):
 import html as _html
 selected=[]
 try:
  form=await request.form()
  selected=[str(x) for x in form.getlist("channels")]
  st=_state()
  matrix={}
  for code,label in CHANNELS:
   if code not in selected:
    continue
   if code=="m99eu":
    key=_env("M99EU_API_KEY")
    base=_env("M99EU_BASE_URL","https://m99.eu")
    status,data=_ps_get(base,key,2041) if key else (None,{})
    prod=data.get("product",data) if isinstance(data,dict) else {}
    identity_ok=(status==200 and str(prod.get("reference","")).replace(" ","")=="M99100018")
    matrix[code]={"label":label,"mode":"UPDATE_EXISTING_2041",
      "status":"AUTO_READY" if identity_ok and not st.get("blockers") else "BLOCKED",
      "details":[] if identity_ok else ["Product 2041 / M99 100018 identity readback failed"]}
   else:
    matrix[code]={"label":label,"mode":"CREATE_OR_UPDATE_AFTER_DUPLICATE_LOOKUP","status":"NEEDS_REVIEW",
      "details":["Channel-specific live write gates are not yet proven in this native screen."]}
  st["matrix"]=matrix;st["selected"]=selected
  st["message"]="Preflight completed inside M99 Knowledge. NO WRITE."
  try:
   return templates.TemplateResponse("r730_knowledge_publish_center.html",{"request":request,**st})
  except Exception as render_exc:
   rows="".join("<tr><td>"+_html.escape(str(v.get("label",k)))+"</td><td>"+_html.escape(str(v.get("mode","")))+"</td><td>"+_html.escape(str(v.get("status","")))+"</td></tr>" for k,v in matrix.items())
   body="<html><head><meta charset='utf-8'><title>M99 Preflight</title></head><body><h1>M99 Knowledge - Preflight</h1><p>Canonical: "+_html.escape(str(st.get("reference","M99 100018")))+"</p><p>Template fallback: "+_html.escape(type(render_exc).__name__+": "+str(render_exc))+"</p><table border='1' cellpadding='8'><tr><th>Channel</th><th>Mode</th><th>Status</th></tr>"+rows+"</table><p><a href='/r730/publish-center'>Back to Publish Center</a></p><p>WRITE_EXECUTED: FALSE</p></body></html>"
   return HTMLResponse(body,status_code=200)
 except Exception as exc:
  body="<html><head><meta charset='utf-8'><title>M99 Preflight Blocked</title></head><body><h1>M99 Knowledge - Preflight BLOCKED</h1><p>"+_html.escape(type(exc).__name__+": "+str(exc))+"</p><p>Selected: "+_html.escape(", ".join(selected))+"</p><p><a href='/r730/publish-center'>Back to Publish Center</a></p><p>WRITE_EXECUTED: FALSE</p></body></html>"
  return HTMLResponse(body,status_code=200)

@router.post("/publish",response_class=HTMLResponse)
async def publish(request:Request):
 import html as _html
 selected=[]
 try:
  form=await request.form();selected=[str(x) for x in form.getlist("channels")];confirm=str(form.get("confirm") or "");st=_state()
  if confirm!="PUBLISH_AUTO_READY":
   st["selected"]=selected;st["message"]="Publish confirmation missing. Nothing written."
   return templates.TemplateResponse("r730_knowledge_publish_center.html",{"request":request,**st})
  results={}
  if "m99eu" in selected:
   from app.services.v073_phase46.r730_r41_controlled_live_publish import controlled_update
   key=_env("M99EU_API_KEY");base=_env("M99EU_BASE_URL","https://m99.eu")
   results["m99eu"]=controlled_update(base,key,st.get("payload") or {}) if key else {"status":"BLOCKED","write":False,"blockers":["M99EU_API_KEY_MISSING"]}
  for code,label in CHANNELS:
   if code in selected and code!="m99eu":results[code]={"status":"NOT_WRITTEN","write":False,"blockers":["NOT_AUTO_READY"]}
  st["selected"]=selected;st["results"]=results;st["matrix"]={}
  for code,label in CHANNELS:
   if code not in selected:continue
   r=results.get(code,{})
   st["matrix"][code]={"label":label,"mode":"UPDATE_EXISTING_2041" if code=="m99eu" else "CREATE_OR_UPDATE_AFTER_DUPLICATE_LOOKUP","status":"PUBLISHED_READBACK_OK" if r.get("status")=="SUCCESS" else r.get("status","NOT_WRITTEN"),"details":r.get("blockers",[])}
  st["message"]="Controlled publish SUCCESS: m99.eu Product #2041 updated hidden + readback verified." if results.get("m99eu",{}).get("status")=="SUCCESS" else "Controlled publish finished fail-closed. Review result; no CREATE fallback."
  return templates.TemplateResponse("r730_knowledge_publish_center.html",{"request":request,**st})
 except Exception as exc:
  body="<html><body><h1>M99 Knowledge - Controlled Publish BLOCKED</h1><p>"+_html.escape(type(exc).__name__+": "+str(exc))+"</p><p>NO CREATE FALLBACK</p><p><a href='/r730/publish-center'>Back</a></p></body></html>"
  return HTMLResponse(body,status_code=200)


@router.get("/recovery", response_class=HTMLResponse)
async def r411_recovery(request: Request):
 import html as _html
 from app.services.v073_phase46.r730_r411_ambiguous_recovery import diagnose
 key=_env("M99EU_API_KEY");base=_env("M99EU_BASE_URL","https://m99.eu")
 result=diagnose(base,key) if key else {"status":"BLOCKED","error":"M99EU_API_KEY_MISSING","safe_to_retry":False,"write_executed":False}
 rows="".join("<tr><th style='text-align:left;padding:8px'>"+_html.escape(str(k))+"</th><td style='padding:8px'>"+_html.escape(str(v))+"</td></tr>" for k,v in result.items())
 body="<!doctype html><html><head><meta charset='utf-8'><title>M99 Recovery</title><style>body{font-family:Arial;margin:35px;background:#f4f6f8}.card{background:white;padding:25px;border-radius:12px}table{width:100%}</style></head><body><div class='card'><h1>M99 Knowledge — R4.1.1 Recovery</h1><p>READ ONLY — recovery GET; no PUT/POST/CREATE.</p><table>"+rows+"</table><p><a href='/r730/publish-center'>Back to Product Publish Center</a></p></div></body></html>"
 return HTMLResponse(body)

