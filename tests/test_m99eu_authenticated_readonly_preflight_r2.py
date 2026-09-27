from types import SimpleNamespace
import pytest
import integrations.m99eu_prestashop.readonly_preflight_r2 as p
def api(get="true",post="true",put="true",delete="true"):return f'<prestashop><api><products get="{get}" post="{post}" put="{put}" delete="{delete}"/></api></prestashop>'
def langs(rows):return "<prestashop><languages>"+"".join(f"<language><id>{i}</id><iso_code>{s}</iso_code><active>{a}</active></language>" for i,s,a in rows)+"</languages></prestashop>"
def cat(i=938):return f'<prestashop><category><id>{i}</id><active>1</active><name><language id="1">Test</language></name></category></prestashop>'
blank="<prestashop><product><id/><name/><reference/></product></prestashop>"
class Fake:
 def __init__(self,responses):self.responses=list(responses);self.calls=[]
 def get(self,path,params=None):self.calls.append(("GET",path));return self.responses.pop(0)
def cfg():return SimpleNamespace(test_category_id=938)
def test_full_contract_arbitrary_language_ids():
 f=Fake([api(),langs([("9","ru","1"),("4","en","1"),("7","bg","1")]),cat(),blank]);r=p.run_preflight(cfg(),f)
 assert r["required_language_map"]=={"en":"4","bg":"7","ru":"9"} and len(r["requests"])==4 and not r["write_allowed"]
def test_get_permission_required():
 f=Fake([api(get="false")])
 with pytest.raises(p.PreflightViolation):p.run_preflight(cfg(),f)
def test_missing_language_blocks():
 f=Fake([api(),langs([("1","en","1"),("2","bg","1")])])
 with pytest.raises(p.PreflightViolation):p.run_preflight(cfg(),f)
def test_inactive_required_language_blocks():
 f=Fake([api(),langs([("1","en","1"),("2","bg","1"),("3","ru","0")])])
 with pytest.raises(p.PreflightViolation):p.run_preflight(cfg(),f)
def test_duplicate_iso_blocks():
 with pytest.raises(p.PreflightViolation):p.languages(langs([("1","en","1"),("2","en","1"),("3","ru","1")]))
def test_wrong_category_blocks():
 f=Fake([api(),langs([("1","en","1"),("2","bg","1"),("3","ru","1")]),cat(939)])
 with pytest.raises(p.PreflightViolation):p.run_preflight(cfg(),f)
def test_missing_blank_schema_blocks():
 f=Fake([api(),langs([("1","en","1"),("2","bg","1"),("3","ru","1")]),cat(),"<prestashop/>"])
 with pytest.raises(p.PreflightViolation):p.run_preflight(cfg(),f)
def test_write_permissions_are_facts_not_authorization():
 x=p.permissions(api(post="true",put="true",delete="true"));assert x["post"] and x["put"] and x["delete"]
def test_transport_rejects_wrong_host():
 with pytest.raises(p.ReadOnlyViolation):p.OneShotBasicGetTransport("https://example.com","X")
def test_transport_rejects_missing_key():
 with pytest.raises(p.ReadOnlyViolation):p.OneShotBasicGetTransport("https://m99.eu","")
def test_transport_rejects_non_api_path():
 t=p.OneShotBasicGetTransport("https://m99.eu","X")
 with pytest.raises(p.ReadOnlyViolation):t.get("/")
