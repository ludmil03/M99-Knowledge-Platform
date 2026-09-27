import pytest
from app.services.bultex99_readonly_hydration import *
def html():
 return """<html><h1>Panda UNO LOW</h1><div>Арт. №: 06100764.36 € 58.90 с ДДС В наличност EN 20345:2022</div></html>"""
def test_golden_readonly_hydration():
 calls=[]
 def get(u): calls.append(u); return 200,u,html()
 r=hydrate_bultex99_product("https://bultex99.com/products/5161-uno-low",get=get)
 assert len(calls)==1 and r.write_performed is False
 assert r.product.supplier_product_id=="5161"
 assert r.product.supplier_sku=="06100764.36"
 assert str(r.product.gross_price_eur)=="58.90"
def test_rejects_http_and_wrong_host_before_network():
 calls=[]
 def get(u): calls.append(u); return 200,u,html()
 for u in ("http://bultex99.com/products/5161-x","https://evil.example/products/5161-x"):
  with pytest.raises(BultexHydrationError,match="BULTEX_URL_NOT_ALLOWED"):hydrate_bultex99_product(u,get=get)
 assert calls==[]
def test_rejects_cross_host_redirect():
 def get(u): return 200,"https://evil.example/products/5161-x",html()
 with pytest.raises(BultexHydrationError,match="BULTEX_URL_NOT_ALLOWED"):hydrate_bultex99_product("https://bultex99.com/products/5161-x",get=get)
def test_non_200_fails_closed():
 def get(u):return 503,u,""
 with pytest.raises(BultexHydrationError,match="BULTEX_HTTP_503"):hydrate_bultex99_product("https://bultex99.com/products/5161-x",get=get)
