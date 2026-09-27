from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
import hashlib, os, ssl, urllib.request, urllib.error

PRODUCT_KEY="PANDA|11720E|5161"
SUPPLIER_GROSS=Decimal("58.90")
CHANNELS={
 "mela99.com":{"platform":"THIRTY_BEES_PS17_COMPAT","languages":("bg","en","ru"),"authorized":True,"ready":True,"credential_env":"MELA99_API_KEY"},
 "rabotni-drehi.com":{"platform":"WORDPRESS","languages":("bg",),"authorized":True,"ready":True,"credential_env":"RABOTNI_DREHI_API_KEY"},
 "m99.eu":{"platform":"PRESTASHOP_9_1_5","languages":("en","bg","ru"),"authorized":True,"ready":True,"credential_env":"M99EU_API_KEY"},
 "medicinski-drehi.com":{"platform":"WORDPRESS","languages":("bg","en","ru"),"authorized":True,"ready":True,"credential_env":"MEDICINSKI_DREHI_API_KEY"},
 "laviro.ro":{"platform":"PRESTASHOP_1_6_1_24","languages":("ro","en"),"authorized":True,"ready":True,"credential_env":"LAVIRO_API_KEY"},
 "alviro.ro":{"platform":"UNPROVEN","languages":("ro",),"authorized":True,"ready":False,"credential_env":None},
 "toplinka.com":{"platform":"SERVICE_SITE","languages":(),"authorized":False,"ready":False,"credential_env":None},
 "dolibarr":{"platform":"ERP","languages":(),"authorized":True,"ready":False,"credential_env":None},
}
def money(v): return str(v.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))
def persistent_margin(product_key=PRODUCT_KEY,supplier_gross=SUPPLIER_GROSS):
    # Stable pseudo-random hundredths of a percent: 1.00..1.70 inclusive.
    seed=f"{product_key}|{money(supplier_gross)}".encode()
    n=int.from_bytes(hashlib.sha256(seed).digest()[:8],"big")
    bp=100+(n%71)
    return Decimal(bp)/Decimal(10000)
def governed_price(product_key=PRODUCT_KEY,supplier_gross=SUPPLIER_GROSS):
    margin=persistent_margin(product_key,supplier_gross)
    return {"margin_percent":str((margin*100).quantize(Decimal("0.01"))),
            "gross_eur":money(supplier_gross*(Decimal("1")-margin)),
            "supplier_gross_eur":money(supplier_gross)}
def target_scope(requested=None):
    req=list(CHANNELS) if requested is None else list(dict.fromkeys(requested))
    authorized=[x for x in req if x in CHANNELS and CHANNELS[x]["authorized"]]
    ready=[x for x in authorized if CHANNELS[x]["ready"]]
    blocked=[x for x in req if x not in ready]
    return {"requested":req,"authorized":authorized,"ready":ready,"blocked":blocked}
def credential_state(channel):
    env=CHANNELS[channel]["credential_env"]
    return "NOT_REQUIRED" if not env else ("PRESENT" if bool(os.environ.get(env)) else "MISSING")
def public_https_probe(channel,timeout=8):
    if channel in {"dolibarr"}: return {"state":"SKIPPED","reason":"not_public_channel"}
    url="https://"+channel+"/"
    req=urllib.request.Request(url,method="GET",headers={"User-Agent":"M99-Channel-Preflight/1.0"})
    try:
        with urllib.request.urlopen(req,timeout=timeout,context=ssl.create_default_context()) as r:
            return {"state":"PASS","status":int(r.status),"final_url":r.geturl(),"method":"GET"}
    except urllib.error.HTTPError as e:
        # HTTPS endpoint exists even if root access is forbidden/not-found.
        return {"state":"REACHABLE_HTTP_ERROR","status":int(e.code),"method":"GET"}
    except Exception as e:
        return {"state":"FAIL","error":type(e).__name__,"method":"GET"}
def build_preflight(requested=None,live_get=False):
    scope=target_scope(requested)
    rows=[]
    for ch in scope["requested"]:
        cfg=CHANNELS.get(ch)
        if not cfg:
            rows.append({"channel":ch,"gate":"BLOCK","reason":"UNKNOWN_TARGET","write_performed":False}); continue
        row={"channel":ch,"platform":cfg["platform"],"languages":list(cfg["languages"]),
             "authorized":cfg["authorized"],"registry_ready":cfg["ready"],
             "credential_state":credential_state(ch),"write_performed":False}
        if not cfg["authorized"] or not cfg["ready"]:
            row.update(gate="BLOCK",reason="NOT_AUTHORIZED_OR_NOT_READY")
        else:
            row.update(gate="PREFLIGHT",reason="REGISTRY_READY")
        if live_get: row["public_https"]=public_https_probe(ch)
        rows.append(row)
    return {"product":"Panda UNO LOW 11720E","identity":"5161","price":governed_price(),
            "scope":scope,"channels":rows,"http_method":"GET_ONLY" if live_get else "OFFLINE",
            "write_performed":False,"operator_write_approval":False}
def safety_gate(report):
    blockers=[]
    if report.get("write_performed"): blockers.append("UNEXPECTED_WRITE")
    for row in report["channels"]:
        if row.get("write_performed"): blockers.append("CHANNEL_WRITE")
        if row["gate"]=="BLOCK" and row["channel"] in report["scope"]["ready"]:
            blockers.append("READY_SCOPE_CONTRADICTION")
    return {"pass":not blockers,"blockers":blockers,"write_allowed":False}
