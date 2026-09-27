from __future__ import annotations
from dataclasses import dataclass,asdict
import base64,socket,ssl,http.client
from urllib.parse import urlparse

class DiagnosticViolation(RuntimeError): pass
@dataclass
class Step:
 name:str; state:str; detail:str=""; http_status:int|None=None

def safe_error(e):
 # Deliberately expose only exception class + errno, never request headers/credentials.
 errno=getattr(e,"errno",None)
 return type(e).__name__+(f":errno={errno}" if errno is not None else "")

def dns_probe(host):
 try:
  rows=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
  ips=sorted({r[4][0] for r in rows})
  return Step("dns","PASS",f"addresses={len(ips)}")
 except Exception as e:return Step("dns","FAIL",safe_error(e))

def tcp_probe(host,timeout):
 try:
  with socket.create_connection((host,443),timeout=timeout): pass
  return Step("tcp_443","PASS")
 except Exception as e:return Step("tcp_443","FAIL",safe_error(e))

def tls_probe(host,timeout):
 try:
  ctx=ssl.create_default_context()
  with socket.create_connection((host,443),timeout=timeout) as raw:
   with ctx.wrap_socket(raw,server_hostname=host) as s:
    proto=s.version() or "unknown"
  return Step("tls","PASS",proto)
 except Exception as e:return Step("tls","FAIL",safe_error(e))

def https_get(host,path,timeout,api_key=None):
 if not path.startswith("/"):raise DiagnosticViolation("path must be absolute")
 conn=None
 try:
  conn=http.client.HTTPSConnection(host,443,timeout=timeout,context=ssl.create_default_context())
  headers={"Accept":"application/xml","User-Agent":"M99-Knowledge-Platform-ReadOnly-Diagnostic/1.0","Connection":"close"}
  if api_key:
   token=base64.b64encode((api_key+":").encode("utf-8")).decode("ascii")
   headers["Authorization"]="Basic "+token
  conn.request("GET",path,headers=headers)
  r=conn.getresponse()
  # Bound read; enough to establish HTTP behavior without dumping content.
  r.read(2048)
  state="PASS" if 200<=r.status<400 else "HTTP_RESPONSE"
  return Step("https_get_auth" if api_key else "https_get_public",state,"GET_ONLY",r.status)
 except Exception as e:
  return Step("https_get_auth" if api_key else "https_get_public","FAIL",safe_error(e))
 finally:
  if conn:
   try:conn.close()
   except:pass

def diagnose(base_url,api_key,timeout=12):
 p=urlparse(base_url)
 if p.scheme!="https" or (p.hostname or "").lower() not in {"m99.eu","www.m99.eu"}:
  raise DiagnosticViolation("diagnostic host must be m99.eu over HTTPS")
 host=p.hostname
 steps=[dns_probe(host),tcp_probe(host,timeout),tls_probe(host,timeout)]
 # No retries. Each HTTP probe is exactly one GET.
 steps.append(https_get(host,"/",timeout,None))
 steps.append(https_get(host,"/api",timeout,None))
 steps.append(https_get(host,"/api",timeout,api_key))
 return {"host":host,"policy":"GET_ONLY_NO_RETRY","credential":"PRESENT_NOT_PRINTED",
         "steps":[asdict(x) for x in steps],"write_performed":False,"write_allowed":False}

def classify(report):
 s={x["name"]:x for x in report["steps"]}
 if s["dns"]["state"]!="PASS":return "DNS_FAILURE"
 if s["tcp_443"]["state"]!="PASS":return "TCP_443_FAILURE"
 if s["tls"]["state"]!="PASS":return "TLS_FAILURE"
 pub=[x for x in report["steps"] if x["name"]=="https_get_public"]
 root,api=pub[0],pub[1]
 auth=s["https_get_auth"]
 if root["state"]=="FAIL":return "PUBLIC_HTTPS_CONNECTION_FAILURE"
 if api["state"]=="FAIL" and auth["state"]=="FAIL":return "API_CONNECTION_RESET_OR_TRANSPORT_FAILURE"
 if auth["http_status"] in (401,403):return "API_AUTH_REJECTED"
 if auth["state"]=="FAIL":return "AUTH_REQUEST_TRANSPORT_FAILURE"
 if auth["http_status"] and 200<=auth["http_status"]<300:return "AUTHENTICATED_API_HTTP_OK"
 return "API_HTTP_RESPONSE_RECEIVED"
