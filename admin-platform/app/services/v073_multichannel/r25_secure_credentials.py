from pathlib import Path
import getpass,json,os
SEC=Path(os.environ.get("LOCALAPPDATA",str(Path.home())))/"M99"/"secure"
FILE=SEC/"channels.credentials.json"
CHANNELS=[
("m99.eu","prestashop","https://m99.eu",["api_key"]),
("mela99.com","prestashop","https://mela99.com",["api_key"]),
("medicinski-drehi.com","prestashop","https://medicinski-drehi.com",["api_key"]),
("rabotni-drehi.com","woocommerce","https://rabotni-drehi.com",["username","app_password"]),
("laviro.ro","prestashop","https://laviro.ro",["api_key"]),
("alviro.ro","prestashop","https://alviro.ro",["api_key"]),
("toplinka.com","woocommerce","https://toplinka.com",["username","app_password"]),
("dolibarr","dolibarr","",["base_url","api_key"])]
def load():
 try:return json.loads(FILE.read_text(encoding="utf-8"))
 except:return {"version":1,"channels":{}}
def main():
 print("M99 R7.3.0 R2.5 SECURE CREDENTIAL SETUP")
 print("Secrets are hidden and stored outside Git.")
 d=load()
 for cid,kind,base,fields in CHANNELS:
  print("\n"+cid+" ("+kind+")")
  if input("Configure/update? [y/N]: ").strip().lower()!="y":continue
  x={"kind":kind,"base_url":base}
  for f in fields:
   v=(input("Base URL: ") if f=="base_url" else getpass.getpass(f.replace("_"," ").title()+": ")).strip()
   if f=="base_url":v=v.rstrip("/")
   if not v:x={};print("[SKIP] empty value");break
   x[f]=v
  if x:d["channels"][cid]=x;print("[OK] stored locally:",cid)
 SEC.mkdir(parents=True,exist_ok=True);FILE.write_text(json.dumps(d,indent=2),encoding="utf-8")
 try:
  import subprocess
  subprocess.run(["icacls",str(FILE),"/inheritance:r","/grant:r",os.getlogin()+":(R,W)"],capture_output=True)
 except:pass
 print("\nCredential file:",FILE);print("Values were not printed. No network. No website write.")
if __name__=="__main__":main()
