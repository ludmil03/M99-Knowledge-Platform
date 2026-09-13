from pathlib import Path
import json,hashlib,zipfile,datetime
ROOT=Path.home()/"Documents/GitHub/M99-Knowledge-Platform";DESKTOP=Path.home()/"Desktop"
EXACT=["admin-platform/app/services/v073_phase45/m99eu_operator_single_publish.py","admin-platform/app/services/v073_phase45/m99eu_r37_auto_publish.py","admin-platform/app/services/v073_phase46/r4_r1_canonical_payload_bridge.py","admin-platform/app/services/v073_phase46/durable_draft_enrichment.py","admin-platform/app/templates/operator_publish/phase46_r1_final.html","admin-platform/app/main.py"]
TERMS=("r1-final","r1_final","m99eu_r37_auto_publish","r4_r1_canonical_payload_bridge","phase46_r1_final","canonical_payload")
def main():
    found=set(EXACT)
    for root in (ROOT/'admin-platform/app/routers',ROOT/'tests'):
        if not root.exists():continue
        for p in root.rglob('*.py'):
            try:t=p.read_text(encoding='utf-8',errors='replace')
            except Exception:continue
            if any(x.casefold() in t.casefold() for x in TERMS):found.add(str(p.relative_to(ROOT)).replace('\\','/'))
    ts=datetime.datetime.now().strftime('%Y%m%d_%H%M%S');out=DESKTOP/f'M99_R7C_PUBLISH_CHAIN_SOURCE_SNAPSHOT_{ts}.zip';manifest=[]
    with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED) as z:
        for rel in sorted(found):
            p=ROOT/rel
            if not p.is_file():continue
            b=p.read_bytes();z.writestr(rel,b);manifest.append({'path':rel,'sha256':hashlib.sha256(b).hexdigest(),'bytes':len(b)})
        z.writestr('SNAPSHOT_MANIFEST.json',json.dumps({'read_only':True,'files':manifest},ensure_ascii=False,indent=2))
    print('[REPORT]',out);print('[FILES]',len(manifest));print('[DONE] Source capture only; no website write.')
if __name__=='__main__':main()
