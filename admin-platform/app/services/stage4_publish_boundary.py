from __future__ import annotations
from dataclasses import dataclass
from decimal import Decimal
from typing import Mapping, Sequence
import hashlib, json, re

M99_ID_RE=re.compile(r"^M99 [0-9]{6}$")
M99EU_LANGUAGES=("en","bg","ru")

@dataclass(frozen=True)
class PublishProduct:
 identity_state:str
 m99_id:str|None
 canonical_name:str
 gross_price:Decimal
 vat_rate:Decimal
 content:Mapping[str,object]
 variants:tuple[str,...]
 target:str

@dataclass(frozen=True)
class PublishPayload:
 operation:str
 target:str
 m99_id:str|None
 reference:str|None
 gross_price:str
 vat_rate:str
 languages:tuple[str,...]
 variants:tuple[str,...]
 scope_token:str
 write_performed:bool=False

def _content_complete(content,langs):
 for lang in langs:
  c=content.get(lang)
  if c is None:return False
  for f in ("name","short","long","meta_title","meta_description"):
   if not str(getattr(c,f,"") if not isinstance(c,dict) else c.get(f,"")).strip():return False
 return True

def build_publish_payload(p:PublishProduct, *, new_m99_id:str|None=None)->PublishPayload:
 state=p.identity_state.upper()
 if p.target!="m99.eu": raise ValueError("ADAPTER_NOT_PROVEN:"+p.target)
 if p.gross_price<=0: raise ValueError("INVALID_GROSS_PRICE")
 if p.vat_rate<0: raise ValueError("INVALID_VAT")
 if not _content_complete(p.content,M99EU_LANGUAGES):raise ValueError("CHANNEL_LANGUAGE_CONTENT_INCOMPLETE")
 if len(set(p.variants))!=len(p.variants):raise ValueError("DUPLICATE_VARIANT")
 if state=="EXISTING":
  mid=p.m99_id
  if not mid or not M99_ID_RE.fullmatch(mid):raise ValueError("EXISTING_M99_ID_INVALID")
  op="UPDATE"
 elif state=="NEW":
  if p.m99_id:raise ValueError("NEW_MUST_NOT_HAVE_EXISTING_M99_ID")
  mid=new_m99_id
  if not mid or not M99_ID_RE.fullmatch(mid):raise ValueError("NEW_REQUIRES_COLLISION_CHECKED_M99_ID_AT_WRITE_BOUNDARY")
  op="CREATE"
 else:raise ValueError("IDENTITY_NOT_READY")
 raw={"operation":op,"target":p.target,"m99_id":mid,"gross_price":str(p.gross_price),"vat_rate":str(p.vat_rate),
      "languages":M99EU_LANGUAGES,"variants":p.variants}
 token=hashlib.sha256(json.dumps(raw,sort_keys=True).encode()).hexdigest()
 return PublishPayload(op,p.target,mid,mid,str(p.gross_price),str(p.vat_rate),M99EU_LANGUAGES,p.variants,token,False)

@dataclass
class SimulatedPS9Adapter:
 calls:list
 def create(self,payload):
  self.calls.append(("POST",payload.reference))
  return {"confirmed":True,"remote_id":"SIM-CREATE-1","scope_token":payload.scope_token}
 def update(self,payload):
  self.calls.append(("PUT",payload.reference))
  return {"confirmed":True,"remote_id":"SIM-UPDATE-1","scope_token":payload.scope_token}
 def readback(self,payload,response):
  self.calls.append(("GET",response["remote_id"]))
  return response.get("scope_token")==payload.scope_token
