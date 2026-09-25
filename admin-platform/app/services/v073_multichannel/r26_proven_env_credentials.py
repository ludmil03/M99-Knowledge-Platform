from __future__ import annotations
import getpass, os, subprocess, sys
CHANNELS=[
 ("m99.eu", [("M99EU_API_KEY","secret"),("M99EU_BASE_URL","default:https://m99.eu")]),
 ("mela99.com",[("M99_MELA99_API_KEY","secret")]),
 ("rabotni-drehi.com",[("M99_RABOTNI_DREHI_COM_USERNAME","text"),("M99_RABOTNI_DREHI_COM_APP_PASSWORD","secret")]),
 ("dolibarr",[("DOLIBARR_BASE_URL","text"),("DOLIBARR_API_KEY","secret")]),
]
def set_user(name,value):
 # setx writes the USER environment for future processes. Never print value.
 p=subprocess.run(["setx",name,value],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 return p.returncode==0
def main():
 print("="*78);print("M99 R7.3.0 R2.6 PROVEN CREDENTIAL BASELINE");print("="*78)
 print("Uses Windows USER environment variables already used by stable M99 runtime.")
 print("Secret values are hidden and never printed.")
 for channel,fields in CHANNELS:
  print("\n["+channel+"]")
  if input("Configure/update this channel? [y/N]: ").strip().lower()!="y":continue
  for name,kind in fields:
   if kind.startswith("default:"):
    default=kind.split(":",1)[1]
    v=input(f"{name} [{default}]: ").strip() or default
   elif kind=="secret":
    v=getpass.getpass(name+": ").strip()
   else:v=input(name+": ").strip()
   if not v: print("[SKIP]",name,"empty");continue
   if not set_user(name,v): print("[FAIL] could not persist",name);return 2
   os.environ[name]=v
   print("[PASS]",name,"stored in Windows USER environment (value hidden)")
 print("\n[PASS] Credential setup completed.")
 print("Close this window after reviewing the status. New processes inherit persisted values.")
 return 0
if __name__=="__main__":raise SystemExit(main())
