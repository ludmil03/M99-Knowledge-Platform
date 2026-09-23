from pathlib import Path
import sys,argparse,json,os,importlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.real_selected_channel_hidden_publish_r7 import *
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--channel",required=True,choices=CHANNELS);p.add_argument("--m99-id",required=True);p.add_argument("--external-id",required=True)
 p.add_argument("--confirm",required=True);p.add_argument("--canonical-json",required=True)
 a=p.parse_args()
 if a.channel!="m99.eu":
  raise SystemExit("[BLOCK] R7 live adapter is currently proven/bound only for m99.eu; selected channel has no R7 verified live adapter yet.")
 # Deliberately no guessed API calls here. The application must expose an existing verified adapter binding.
 try:
  mod=importlib.import_module("integrations.m99eu_prestashop9.r7_live_adapter")
 except Exception:
  raise SystemExit("[BLOCK] Verified R7 m99.eu live adapter binding not found. No write performed.")
 required=("preflight_existing","update_hidden","readback_existing")
 if not all(hasattr(mod,n) for n in required):raise SystemExit("[BLOCK] R7 adapter contract incomplete. No write performed.")
 r=LivePublishRequest(a.channel,a.m99_id,a.external_id,a.confirm,True,True,True,True,True,True,True,True)
 canonical=json.loads(Path(a.canonical_json).read_text(encoding="utf-8"))
 out=execute_live_hidden_update(r,canonical,mod.preflight_existing,mod.update_hidden,mod.readback_existing)
 print(json.dumps(out,ensure_ascii=False,indent=2))
 if out["status"]!="LIVE_HIDDEN_UPDATE_VERIFIED":raise SystemExit(3)
if __name__=="__main__":main()
