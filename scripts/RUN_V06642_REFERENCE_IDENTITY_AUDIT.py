from pathlib import Path
import json
ROOT=Path(".")
src=ROOT/"output/diadora_s3s_v06642_live_analysis_preview.json"
out=ROOT/"output/diadora_s3s_v06642_reference_identity_audit.json"
p2076="M99-REF"; p2100=None
if src.exists():
    d=json.loads(src.read_text(encoding="utf-8"))
    c=d.get("product_comparison",{})
    p2076=c.get("product_2076",{}).get("reference",p2076)
    p2100=c.get("product_2100",{}).get("reference",p2100)
def cls(v):
    raw=(v or "").strip()
    if not raw:return "MISSING"
    if raw.casefold().replace(" ","") in {"m99-ref","m99ref"}:return "INVALID_PLACEHOLDER"
    return "VALID_OR_LEGACY"
result={"2076_reference":p2076,"2076_status":cls(p2076),"2100_reference":p2100,"2100_status":cls(p2100),"canonical_productgroup":"M99 100017","manufacturer_item":"701.183119_80013","supplier_reference":"06100768","writes":False}
out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("2076 reference:",p2076,"=>",result["2076_status"])
print("2100 reference:",p2100,"=>",result["2100_status"])
print("Canonical ProductGroup: M99 100017")
print("Writes to websites: NO")
print("Output:",out)
