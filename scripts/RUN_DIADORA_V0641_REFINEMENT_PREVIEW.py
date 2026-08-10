from pathlib import Path
import json
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from core.content_claims import build_claim_policy
from core.content_seo_preview import build_diadora_content_preview
from core.content_quality_guard import evaluate_all_content
from core.claim_traceability import build_claim_trace
from core.channel_content_profiles import CHANNEL_CONTENT_PROFILES

ROOT=Path(".")
FIXTURE=ROOT/"tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
V064=ROOT/"output/diadora_glove_abox_low_pro_s1ps_v064_preview.json"
OUTPUT=ROOT/"output/diadora_glove_abox_low_pro_s1ps_v0641_preview.json"
source=json.loads(FIXTURE.read_text(encoding="utf-8")); m=source["manufacturer_evidence"]
canonical=build_canonical_product_facts(m["source_name"],m["source_url"],m["facts"]); facts=canonical_values(canonical)
policy=build_claim_policy(facts); content=build_diadora_content_preview(facts); quality=evaluate_all_content(content,facts); trace=build_claim_trace(canonical,policy)
preview=json.loads(V064.read_text(encoding="utf-8")) if V064.exists() else {"productgroup":{"m99_id":source["m99_id"],"name":source["name"],"brand":source["brand"]},"review":{}}
preview.update({"schema_version":"0.6.4.1","mode":"CONTENT_QUALITY_REFINEMENT","canonical_product_facts":canonical,"content_claim_policy":policy,"channel_content_profiles":CHANNEL_CONTENT_PROFILES,"content_seo_preview":content,"claim_traceability":trace,"content_quality":quality,"writes":{"dolibarr":False,"channels":False,"supplier":False}})
r=preview.setdefault("review",{}); r["content_seo_status"]=quality["status"]; r["content_quality_status"]=quality["status"]; r["publication_status"]="BLOCKED_PENDING_EXISTING_PRODUCT_VERIFICATION"; r["operator_required"]=True
OUTPUT.parent.mkdir(parents=True,exist_ok=True); OUTPUT.write_text(json.dumps(preview,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("M99 Content Quality Refinement v0.6.4.1"); print("=======================================")
print("Product:",source["name"]); print("M99 ID:",source["m99_id"]); print("Canonical facts:",len(canonical["facts"])); print("Derived safe claims:",len(policy["derived_safe_claims"])); print("Claim traces:",len(trace)); print("Content quality:",quality["status"])
for x in quality["results"]: print(" -",x["channel"],x["language"],"=>",x["status"],"| FAQ:",len(content[x["channel"]][x["language"]]["faq"]),"| issues:",x["issues"] or "NONE")
print("Publication enabled: NO"); print("Writes to Dolibarr: NO"); print("Writes to websites: NO"); print("Preview written to:",OUTPUT)
