from pathlib import Path
import json
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from core.content_seo_preview import build_diadora_content_preview
from core.content_quality_guard import evaluate_all_content
from core.claim_traceability import build_claim_trace

ROOT=Path(".")
FIXTURE=ROOT/"tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
V063=ROOT/"output/diadora_glove_abox_low_pro_s1ps_v063_preview.json"
OUTPUT=ROOT/"output/diadora_glove_abox_low_pro_s1ps_v064_preview.json"

source=json.loads(FIXTURE.read_text(encoding="utf-8"))
manufacturer=source["manufacturer_evidence"]
canonical=build_canonical_product_facts(manufacturer["source_name"],manufacturer["source_url"],manufacturer["facts"])
facts=canonical_values(canonical)
content=build_diadora_content_preview(facts)
quality=evaluate_all_content(content,facts)
trace=build_claim_trace(canonical)

if V063.exists():
    preview=json.loads(V063.read_text(encoding="utf-8"))
else:
    preview={"productgroup":{"m99_id":source["m99_id"],"name":source["name"],"brand":source["brand"]},"review":{}}

preview["schema_version"]="0.6.4"
preview["mode"]="CONTENT_QUALITY_EVIDENCE_GUARD"
preview["canonical_product_facts"]=canonical
preview["content_seo_preview"]=content
preview["claim_traceability"]=trace
preview["content_quality"]=quality
preview["writes"]={"dolibarr":False,"channels":False,"supplier":False}
review=preview.setdefault("review",{})
review["content_seo_status"]=quality["status"]
review["content_quality_status"]=quality["status"]
review["publication_status"]="BLOCKED_PENDING_EXISTING_PRODUCT_VERIFICATION"
review["operator_required"]=True

OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(preview,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print("M99 Content Quality & Evidence Guard v0.6.4")
print("============================================")
print("Product:",source["name"])
print("M99 ID:",source["m99_id"])
print("Canonical facts:",len(canonical["facts"]))
print("Claim traces:",len(trace))
print("Content quality:",quality["status"])
for result in quality["results"]:
    print(" -",result["channel"],result["language"],"=>",result["status"],"| issues:",result["issues"] or "NONE")
print("Publication enabled: NO")
print("Writes to Dolibarr: NO")
print("Writes to websites: NO")
print("Preview written to:",OUTPUT)
