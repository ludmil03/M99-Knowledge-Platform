from __future__ import annotations
import base64,http.client,ssl
from urllib.parse import urlparse
class WriteViolation(RuntimeError):pass
class AmbiguousWrite(RuntimeError):pass
class OneShotPS9WriteTransport:
 def __init__(self,base_url,api_key,timeout=20):
  p=urlparse(base_url)
  if p.scheme!="https" or (p.hostname or "").lower() not in {"m99.eu","www.m99.eu"}:raise WriteViolation("m99.eu HTTPS only")
  if not api_key:raise WriteViolation("API key missing")
  self.host=p.hostname;self.api_key=api_key;self.timeout=timeout;self.calls=[]
 def _headers(self,content=False):
  token=base64.b64encode((self.api_key+":").encode()).decode()
  h={"Accept":"application/xml","Authorization":"Basic "+token,"User-Agent":"M99-Knowledge-Platform-Publish/1.0","Connection":"close"}
  if content:h["Content-Type"]="application/xml; charset=utf-8"
  return h
 def request_once(self,method,path,body=None):
  if method not in {"POST","PUT","GET"} or not path.startswith("/api/"):raise WriteViolation("method/path blocked")
  conn=http.client.HTTPSConnection(self.host,443,timeout=self.timeout,context=ssl.create_default_context());self.calls.append((method,path))
  try:
   conn.request(method,path,body=(body.encode("utf-8") if isinstance(body,str) else body),headers=self._headers(method!="GET"))
   r=conn.getresponse();data=r.read(2_000_000)
   if r.status<200 or r.status>=300:raise WriteViolation(f"HTTP {r.status}")
   return data.decode("utf-8-sig",errors="strict")
  except (TimeoutError,ConnectionError,OSError,http.client.HTTPException) as exc:
   raise AmbiguousWrite("AMBIGUOUS_WRITE_STOP_NO_RETRY") from exc
  finally:conn.close()
