from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from core.cherokee_real_publish_v0675 import preflight,real_write
from datetime import datetime,timezone

def save(kind,data):
 d=ROOT/'output'/'v0675_cherokee_real_publish'; d.mkdir(parents=True,exist_ok=True)
 p=d/(datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')+'_'+kind+'.json'); p.write_text(json.dumps(data,ensure_ascii=False,indent=2,default=str),encoding='utf-8'); return p
mode=(sys.argv[1] if len(sys.argv)>1 else 'preflight').lower()
print('M99 v0.6.7.5 - CHEROKEE WW601 REAL PRODUCT PUBLISH')
print('m99.eu: TASK ONLY - NO PRODUCT WRITE (temporary technical problems)')
if mode=='preflight': r=preflight(ROOT)
elif mode=='write': r=real_write(ROOT)
else: raise SystemExit('Use preflight or write')
p=save(mode.upper(),r)
print(json.dumps(r,ensure_ascii=False,indent=2,default=str)); print('Output:',p)
if mode=='preflight' and not r.get('ready'): raise SystemExit(2)
