from pathlib import Path
import sys,argparse,json
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT/"admin-platform"))
from app.services.v073_phase46.operator_selected_channel_publish_r6 import *
def main():
 p=argparse.ArgumentParser(description="R7K.4 R6 operator-selected channel publish preflight")
 p.add_argument("--channel",required=True,choices=ALLOWED_CHANNELS)
 p.add_argument("--m99-id",required=True); p.add_argument("--external-id",required=True)
 p.add_argument("--confirm",default="")
 a=p.parse_args()
 r=PublishRequest(a.m99_id,a.channel,a.external_id,"UPDATE_ONLY",a.confirm)
 print(json.dumps({"schema":SCHEMA,"selected_channel":a.channel,"m99_id":a.m99_id,
   "external_product_id":a.external_id,"expected_confirmation":expected_confirmation(r),
   "note":"This launcher is PREFLIGHT ONLY. Live write is enabled only through a verified channel adapter after all R6 gates are supplied by the application.",
   "write_performed":False},ensure_ascii=False,indent=2))
if __name__=="__main__":main()
