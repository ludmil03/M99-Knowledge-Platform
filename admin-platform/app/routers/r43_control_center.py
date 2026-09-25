from fastapi import APIRouter
from fastapi.responses import HTMLResponse,JSONResponse
import os,sys,json,socket
router=APIRouter()
PUBLISH="/r730/publish-center"
def diag():
 s=socket.socket();s.settimeout(.1)
 try: listening=s.connect_ex(("127.0.0.1",8070))==0
 finally:s.close()
 keys=("M99EU_API_KEY","M99_MELA99_API_KEY","M99_RABOTNI_DREHI_COM_APP_PASSWORD","DOLIBARR_API_KEY")
 return {"version":"R4.3","port_8070":"LISTENING" if listening else "NOT_LISTENING","python":sys.version.split()[0],"publish_center":PUBLISH,"credentials":{k:("CONFIGURED" if os.environ.get(k) else "NOT_IN_PROCESS_ENV") for k in keys},"secrets_exposed":False}
def page(title,body):
 return HTMLResponse("""<!doctype html><meta charset=utf-8><style>body{font-family:Arial;background:#f3f5f7;margin:0}.n{background:#17212b;padding:15px}.n a{color:white;margin-right:20px}main{max-width:1100px;margin:auto;padding:28px}.c{background:white;padding:20px;margin:14px 0;border-radius:12px}</style><div class=n><a href='/r43/control-center'>Control Center</a><a href='/r730/publish-center'>Product Publish Center</a><a href='/r43/diagnostics'>Diagnostics</a><a href='/r43/updates'>Updates</a></div><main><h1>"""+title+"</h1>"+body+"</main>")
@router.get("/r43/control-center",response_class=HTMLResponse)
async def cc():
 return page("M99 Knowledge — Control Center","<div class=c><h2>Runtime</h2><p>Deterministic Runtime Manager controls START/STOP; the web server never kills itself.</p></div><div class=c><h2>Diagnostics</h2><a href='/r43/diagnostics'>Open diagnostics</a></div><div class=c><h2>Updates / Repair</h2><a href='/r43/updates'>Open update status</a></div><div class=c><h2>Publish</h2><a href='/r730/publish-center'>Open Product Publish Center</a><p>Existing R4.1/R4.1.1 publish/recovery engine is preserved.</p></div>")
@router.get("/r43/diagnostics",response_class=HTMLResponse)
async def du():return page("System Diagnostics","<div class=c><pre>"+json.dumps(diag(),ensure_ascii=False,indent=2)+"</pre></div>")
@router.get("/r43/diagnostics.json")
async def dj():return JSONResponse(diag())
@router.get("/r43/updates",response_class=HTMLResponse)
async def up():return page("Update / Repair Center","<div class=c><b>Installed control layer: R4.3</b><p>Fail-closed. No Git operation from this page.</p></div>")
@router.get("/r43/health")
async def health():return {"status":"ok","version":"R4.3","publish_center":PUBLISH,"secrets_exposed":False}
