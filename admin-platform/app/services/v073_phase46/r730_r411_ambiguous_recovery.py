from __future__ import annotations
import base64,socket
from urllib.request import Request as UrlRequest,urlopen
from urllib.error import HTTPError,URLError
from xml.etree import ElementTree as ET
PRODUCT_ID=2041
def _auth(k):return "Basic "+base64.b64encode((k+":").encode()).decode()
def _request(url,key,method="GET",body=None):
 h={"Authorization":_auth(key),"Accept":"application/xml","User-Agent":"M99-Knowledge-R4.1.1"}
 if body is not None:h["Content-Type"]="application/xml"
 try:
  with urlopen(UrlRequest(url,data=body,headers=h,method=method),timeout=30) as r:return {"ok":True,"status":int(getattr(r,"status",200)),"body":r.read(),"error":""}
 except HTTPError as e:return {"ok":False,"status":int(e.code),"body":e.read(),"error":"HTTPError:"+str(e)}
 except (ConnectionResetError,ConnectionAbortedError,BrokenPipeError,TimeoutError,socket.timeout,URLError,OSError) as e:return {"ok":False,"status":0,"body":b"","error":type(e).__name__+":"+str(e)}
def _state(xml):
 root=ET.fromstring(xml);p=root.find("product") if root.tag!="product" else root
 if p is None:raise RuntimeError("PRODUCT_XML_MISSING")
 t=lambda n:((p.find(n).text or "").strip() if p.find(n) is not None else "")
 s={x:t(x) for x in ("id","reference","active","available_for_order","visibility")};b=[]
 if s["id"]!="2041":b.append("ID_MISMATCH")
 if s["reference"].replace(" ","")!="M99100018":b.append("REFERENCE_MISMATCH")
 if s["active"] not in ("0",""):b.append("ACTIVE_NOT_ZERO")
 if s["available_for_order"] not in ("0",""):b.append("ORDERABLE_NOT_ZERO")
 if s["visibility"] not in ("none",""):b.append("VISIBILITY_NOT_NONE")
 return not b,b,s
def diagnose(base,key,transport=_request):
 r=transport(base.rstrip("/")+"/api/products/2041",key,"GET",None)
 if not r.get("ok"):return {"status":"TRANSPORT_BLOCKED","phase":"RECOVERY_GET","write_executed":False,"safe_to_retry":False,"error":r.get("error","")}
 try:ok,b,s=_state(r["body"])
 except Exception as e:return {"status":"READBACK_UNPARSEABLE","phase":"RECOVERY_GET","write_executed":False,"safe_to_retry":False,"error":type(e).__name__+":"+str(e)}
 return {"status":"RECOVERED_READBACK_OK" if ok else "READBACK_BLOCKED","phase":"RECOVERY_GET","write_executed":False,"safe_to_retry":ok,"blockers":b,"state":s}
def guarded_put(base,key,payload,transport=_request):
 url=base.rstrip("/")+"/api/products/2041";pre=transport(url,key,"GET",None)
 if not pre.get("ok"):return {"status":"BLOCKED_PREWRITE_GET","write_executed":False,"safe_to_retry":False}
 try:ok,b,s=_state(pre["body"])
 except Exception as e:return {"status":"BLOCKED_PREWRITE_PARSE","write_executed":False,"safe_to_retry":False,"error":str(e)}
 if not ok:return {"status":"BLOCKED_IDENTITY_OR_SAFETY","write_executed":False,"safe_to_retry":False,"blockers":b}
 put=transport(url,key,"PUT",payload)
 if not put.get("ok"):
  rec=transport(url,key,"GET",None)
  out={"status":"AMBIGUOUS_WRITE","write_executed":True,"ambiguous":True,"safe_to_retry":False,"put_error":put.get("error","")}
  if rec.get("ok"):
   try:rok,rb,rs=_state(rec["body"]);out.update({"recovery_readback_ok":rok,"recovery_blockers":rb,"state":rs})
   except Exception as e:out["recovery_parse_error"]=str(e)
  else:out["recovery_get_error"]=rec.get("error","")
  return out
 post=transport(url,key,"GET",None)
 if not post.get("ok"):return {"status":"WRITE_ACKNOWLEDGED_READBACK_FAILED","write_executed":True,"ambiguous":True,"safe_to_retry":False,"readback_error":post.get("error","")}
 ok,b,s=_state(post["body"]);return {"status":"SUCCESS_READBACK_OK" if ok else "WRITE_READBACK_BLOCKED","write_executed":True,"safe_to_retry":False,"blockers":b,"state":s}
