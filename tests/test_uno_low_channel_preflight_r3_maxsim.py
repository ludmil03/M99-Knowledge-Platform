from decimal import Decimal
import inspect
import integrations.channel_preflight.uno_low_preflight as m

class Resp:
    status=200
    def geturl(self): return "https://m99.eu/"
    def __enter__(self): return self
    def __exit__(self,*a): return False

def test_all_registry_states():
    s=m.target_scope()
    assert set(s["ready"])=={"mela99.com","rabotni-drehi.com","m99.eu","medicinski-drehi.com","laviro.ro"}
    assert set(s["blocked"])=={"alviro.ro","toplinka.com","dolibarr"}

def test_subset_never_expands_targets():
    s=m.target_scope(["m99.eu"])
    assert s["requested"]==["m99.eu"] and s["ready"]==["m99.eu"]

def test_duplicate_request_deduplicated():
    assert m.target_scope(["m99.eu","m99.eu"])["requested"]==["m99.eu"]

def test_unknown_target_fail_closed():
    r=m.build_preflight(["does-not-exist.invalid"])
    assert r["channels"][0]["gate"]=="BLOCK"
    assert not r["scope"]["ready"]

def test_blocked_target_never_becomes_ready():
    for ch in ("alviro.ro","toplinka.com","dolibarr"):
        assert ch not in m.target_scope([ch])["ready"]

def test_no_write_in_every_offline_channel():
    r=m.build_preflight()
    assert not r["write_performed"]
    assert not r["operator_write_approval"]
    assert all(not x["write_performed"] for x in r["channels"])
    assert m.safety_gate(r)["write_allowed"] is False

def test_safety_gate_detects_report_write():
    r=m.build_preflight(["m99.eu"]); r["write_performed"]=True
    g=m.safety_gate(r)
    assert not g["pass"] and "UNEXPECTED_WRITE" in g["blockers"]

def test_safety_gate_detects_channel_write():
    r=m.build_preflight(["m99.eu"]); r["channels"][0]["write_performed"]=True
    g=m.safety_gate(r)
    assert not g["pass"] and "CHANNEL_WRITE" in g["blockers"]

def test_price_deterministic_many_runs():
    vals=[m.governed_price() for _ in range(1000)]
    assert all(x==vals[0] for x in vals)

def test_price_governance_range():
    p=m.governed_price()
    assert Decimal("1.00") <= Decimal(p["margin_percent"]) <= Decimal("1.70")
    assert Decimal("57.90") <= Decimal(p["gross_eur"]) <= Decimal("58.31")

def test_margin_domain_across_many_inputs():
    for cents in range(100,10000,37):
        margin=m.persistent_margin("X",Decimal(cents)/100)
        assert Decimal("0.0100") <= margin <= Decimal("0.0170")

def test_get_only_source_contract():
    src=inspect.getsource(m.public_https_probe)
    assert 'method="GET"' in src
    for forbidden in ('method="POST"','method="PUT"','method="PATCH"','method="DELETE"'):
        assert forbidden not in src

def test_get_probe_success_mock(monkeypatch):
    monkeypatch.setattr(m.urllib.request,"urlopen",lambda *a,**k:Resp())
    x=m.public_https_probe("m99.eu")
    assert x["state"]=="PASS" and x["status"]==200 and x["method"]=="GET"

def test_get_probe_network_failure_fail_closed(monkeypatch):
    def boom(*a,**k): raise TimeoutError("simulated")
    monkeypatch.setattr(m.urllib.request,"urlopen",boom)
    x=m.public_https_probe("m99.eu")
    assert x["state"]=="FAIL" and x["method"]=="GET"

def test_credentials_are_presence_only(monkeypatch):
    secret="SUPER_SECRET_MUST_NOT_LEAK"
    monkeypatch.setenv("M99EU_API_KEY",secret)
    assert m.credential_state("m99.eu")=="PRESENT"
    r=m.build_preflight(["m99.eu"])
    assert secret not in repr(r)

def test_language_ids_are_not_invented():
    r=m.build_preflight()
    text=repr(r)
    assert "language_id" not in text and "id_lang" not in text
