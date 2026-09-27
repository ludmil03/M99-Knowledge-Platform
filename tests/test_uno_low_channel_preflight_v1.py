from integrations.channel_preflight.uno_low_preflight import *
def test_ready_scope():
 r=target_scope()
 assert set(r["ready"])=={"mela99.com","rabotni-drehi.com","m99.eu","medicinski-drehi.com","laviro.ro"}
 assert {"alviro.ro","toplinka.com","dolibarr"}.issubset(set(r["blocked"]))
def test_language_policy():
 assert CHANNELS["m99.eu"]["languages"]==("en","bg","ru")
 assert CHANNELS["mela99.com"]["languages"]==("bg","en","ru")
 assert CHANNELS["medicinski-drehi.com"]["languages"]==("bg","en","ru")
 assert CHANNELS["laviro.ro"]["languages"]==("ro","en")
def test_price_persistent_and_in_range():
 a=governed_price(); b=governed_price()
 assert a==b
 assert Decimal("1.00")<=Decimal(a["margin_percent"])<=Decimal("1.70")
 assert Decimal("57.90")<=Decimal(a["gross_eur"])<=Decimal("58.31")
def test_price_changes_when_supplier_price_changes():
 assert persistent_margin(supplier_gross=Decimal("58.90"))==persistent_margin(supplier_gross=Decimal("58.90"))
 # persistence key includes supplier price; governed record is recalculated on source-price change
 assert governed_price(supplier_gross=Decimal("60.00"))["supplier_gross_eur"]=="60.00"
def test_no_write_offline():
 r=build_preflight()
 assert r["write_performed"] is False and r["operator_write_approval"] is False
 assert safety_gate(r)["pass"] and safety_gate(r)["write_allowed"] is False
def test_blocked_targets_fail_closed():
 r=build_preflight(["alviro.ro","toplinka.com","dolibarr"])
 assert not r["scope"]["ready"]
 assert all(x["gate"]=="BLOCK" for x in r["channels"])
def test_unknown_target_blocked():
 r=build_preflight(["unknown.example"])
 assert r["channels"][0]["gate"]=="BLOCK"
def test_live_mode_contract_get_only():
 r=build_preflight(["m99.eu"],live_get=False)
 assert r["http_method"]=="OFFLINE"
 import inspect
 src=inspect.getsource(public_https_probe)
 assert 'method="GET"' in src
 assert "POST" not in src and "PUT" not in src and "DELETE" not in src and "PATCH" not in src
