from pathlib import Path
import pytest
from app.services.v073_multichannel import readonly_adapters_r231 as a
REPO=Path('X'); ADMIN=Path('Y')
def test_constants(): assert a.REFERENCE=='M99 100018' and a.KNOWN_M99EU_ID==2041
def test_get_only_source():
 s=Path(a.__file__).read_text(encoding='utf-8'); assert "method='GET'" in s
 for method in ('POST','PUT','PATCH','DELETE'): assert "method='"+method+"'" not in s
def test_ps_zero(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':True,'status':200,'json':{'products':[]}}); assert a._ps_lookup('https://x','k','M99 100018')['products']==[]
def test_ps_one(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':True,'status':200,'json':{'products':[{'id':2041,'reference':'M99 100018'}]}}); assert a._ps_lookup('https://x','k','M99 100018')['products'][0]['id']==2041
def test_ps_many(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':True,'status':200,'json':{'products':[{'id':1},{'id':2}]}}); assert len(a._ps_lookup('https://x','k','r')['products'])==2
def test_wc(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':True,'status':200,'json':[{'id':7,'sku':'M99 100018','variations':[],'images':[]}]}); assert a._wc_lookup('https://x','k','s','M99 100018')['products'][0]['id']==7
def test_dolibarr_exact(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':True,'status':200,'json':[{'id':8,'ref':'M99 100018'},{'id':9,'ref':'OTHER'}]}); assert len(a._dolibarr_lookup('https://x','k','M99 100018')['products'])==1
def test_http_failure(monkeypatch):
 monkeypatch.setattr(a,'_get_json',lambda *x,**k:{'ok':False,'status':401,'error':'HTTP_ERROR'}); assert a._ps_lookup('https://x','k','r')['connectivity']['error']=='HTTP_ERROR'
