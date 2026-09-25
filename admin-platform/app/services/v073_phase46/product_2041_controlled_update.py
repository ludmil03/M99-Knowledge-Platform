from decimal import Decimal,ROUND_HALF_UP
from hashlib import sha256
PRODUCT_ID="2041";REFERENCE="M99 100018";CONFIRMATION="UPDATE M99 100018 PRODUCT 2041 ON M99.EU"
def price(supplier,revision,gross):
 p=Decimal(str(gross));u=1000+(int.from_bytes(sha256(f"{REFERENCE}|{supplier}|{revision}|{p}|PRC-004".encode()).digest()[:4],"big")%701);d=Decimal(u)/Decimal(100000);g=(p*(1-d)).quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
 if p<=0 or g>=p:raise ValueError("PRICE_BLOCK")
 return d,g
def preflight(state,verified,supplier,revision,gross,vat,tax,variants,images):
 b=[]
 if str(state.get("id"))!=PRODUCT_ID:b+=["PRODUCT_ID"]
 if state.get("reference")!=REFERENCE:b+=["REFERENCE"]
 if (state.get("active"),state.get("available_for_order"),state.get("visibility"))!=("0","0","none"):b+=["HIDDEN"]
 if not verified:b+=["SUPPLIER"]
 if int(tax or 0)<=0 or Decimal(str(vat))<=0:b+=["VAT"]
 if variants<=0:b+=["VARIANTS"]
 if images<=0:b+=["IMAGES"]
 d=g=n=None
 if not b:
  try:d,g=price(supplier,revision,gross);n=(g/(1+Decimal(str(vat)))).quantize(Decimal(".01"),rounding=ROUND_HALF_UP)
  except ValueError:b+=["PRICE"]
 return {"ready":not b,"blockers":b,"discount":d,"gross":g,"net":n,"tax":str(tax),"operation":"UPDATE","id":PRODUCT_ID}
def authorize(p,c):
 if not p["ready"] or c!=CONFIRMATION:raise ValueError("BLOCKED")
def readback(p,a):
 b=[]
 if (str(a.get("id")),a.get("reference"))!=(PRODUCT_ID,REFERENCE):b+=["IDENTITY"]
 if (a.get("active"),a.get("available_for_order"),a.get("visibility"))!=("0","0","none"):b+=["HIDDEN"]
 if str(a.get("tax"))!=p["tax"]:b+=["VAT"]
 if Decimal(str(a.get("gross","-1")))!=p["gross"]:b+=["GROSS"]
 if int(a.get("default_count",0))!=1:b+=["DEFAULT"]
 if int(a.get("variant_count",0))<=0:b+=["VARIANTS"]
 if int(a.get("image_count",0))<=0:b+=["IMAGES"]
 return not b,tuple(b)
def execute(p,c,update_product,upload_images,sync_variants,fetch):
 authorize(p,c);update_product(PRODUCT_ID,{"reference":REFERENCE,"price_net":str(p["net"]),"tax":p["tax"],"active":"0","available_for_order":"0","visibility":"none"});upload_images(PRODUCT_ID);sync_variants(PRODUCT_ID);return readback(p,fetch(PRODUCT_ID))
