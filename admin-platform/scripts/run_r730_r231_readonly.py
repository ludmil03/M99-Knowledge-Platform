from pathlib import Path
import json
from app.services.v073_multichannel.readonly_adapters_r231 import run
REPO=Path(r'C:\Users\user\Documents\GitHub\M99-Knowledge-Platform'); ADMIN=REPO/'admin-platform'
def main():
 print('='*78);print('M99 R7.3.0 R2.3.1 REAL READ-ONLY CHANNEL ADAPTERS / GET ONLY');print('='*78)
 report=run(REPO,ADMIN,'M99 100018')
 for row in report['channels']:
  print('\n['+row['channel_id']+']',row['decision']);print(' platform:',row['platform'],row['version']);print(' credentials_present:',row['credentials_present'])
  if row['lookup']:
   print(' connectivity:',row['lookup']['connectivity']);print(' exact products:',len(row['lookup']['products']))
   for product in row['lookup']['products']: print(' product:',product)
  if row['blockers']: print(' blockers:',', '.join(row['blockers']))
 out=Path.home()/'Desktop'/'M99_R730_R231_REAL_READONLY_CHANNEL_REPORT.json';out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print('\n[PASS] R2.3.1 COMPLETE / GET ONLY / WRITE FALSE');print('Report:',out);return 0
if __name__=='__main__': raise SystemExit(main())
