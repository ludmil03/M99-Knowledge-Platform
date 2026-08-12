import re
from datetime import datetime,timezone
def norm(v): return re.sub(r"[^a-z0-9]+","",str(v).lower())
def resolve(manufacturer,suppliers):
    m=[x for x in manufacturer if x not in (None,"")]
    s=[x for x in suppliers if x not in (None,"")]
    if m:
        conflict=[x for x in s if norm(x)!=norm(m[0])]
        return {"selected":m[0],"status":"SOURCE_CONFLICT" if conflict else "VERIFIED","conflicts":conflict}
    if s and len({norm(x) for x in s})==1:
        return {"selected":s[0],"status":"SUPPLIER_CONSENSUS","conflicts":[]}
    return {"selected":None,"status":"SOURCE_CONFLICT" if s else "UNVERIFIED","conflicts":s}
def commercial(supplier,url,price=None,currency=None,promo=None,stock=None,sizes=None):
    return {"supplier":supplier,"url":url,"observed_at_utc":datetime.now(timezone.utc).isoformat(),
    "raw_price":{"value":price,"currency":currency},"promo_price":{"value":promo,"currency":currency},
    "availability":stock,"size_availability":sizes or [],"m99_selling_price":None}
def evidence_pack(manufacturer,suppliers):
    return {"manufacturer":manufacturer,"suppliers":suppliers,
    "ai_rules":{"supported_facts_only":True,"no_verbatim_copy":True,"no_invented_stock_price_material_standard":True}}
