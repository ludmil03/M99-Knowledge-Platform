from fastapi import APIRouter
from fastapi.responses import HTMLResponse,JSONResponse
import os,sys,json
router=APIRouter()
def snap():
 return {"runtime":"M99 R7.3.0 R4.2","python":sys.version.split()[0],"publish_center":"/r730/publish-center","credentials":{k:("CONFIGURED" if os.environ.get(k) else "NOT_IN_PROCESS_ENV") for k in ("M99EU_API_KEY","M99_MELA99_API_KEY","M99_RABOTNI_DREHI_COM_APP_PASSWORD","DOLIBARR_API_KEY")},"secrets_exposed":False}
@router.get("/r42/system-diagnostics.json")
async def dj():return JSONResponse(snap())
@router.get("/r42/system-diagnostics",response_class=HTMLResponse)
async def dh():
 d=snap(); rows="".join("<tr><th>"+k+"</th><td><pre>"+json.dumps(v,ensure_ascii=False,indent=2)+"</pre></td></tr>" for k,v in d.items())
 return HTMLResponse("<!doctype html><meta charset=utf-8><h1>M99 Knowledge — System Diagnostics</h1><p>READ ONLY. Secrets are never displayed.</p><table>"+rows+"</table><p><a href='/r730/publish-center'>Product Publish Center</a></p>")
