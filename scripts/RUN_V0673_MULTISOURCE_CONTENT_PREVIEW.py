from pathlib import Path
from datetime import datetime,timezone
import json
from core.cherokee_canonical_merge_v0672 import parse_manufacturer,parse_stenso,build_canonical
from core.multisource_content_engine_v0673 import supplier_market_evidence,build_claim_registry,evidence_model,preview
ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); out=Path("output/v0673_multisource_content");out.mkdir(parents=True,exist_ok=True)
m=parse_manufacturer();s=parse_stenso();c=build_canonical(m,s);market=supplier_market_evidence();claims=build_claim_registry(market);model=evidence_model(claims,market);docs=preview(model)
report={"schema_version":"0.6.7.3","http_policy":"GET_ONLY","canonical_product":c,"supplier_market_evidence":market,"claim_registry":claims,"content_evidence_model":model,"language_documents":docs,
"language_policy":{"BG_SITES":["bg","en","ru"],"RO_SITES":["ro","en"]},"ai_evidence_contract":"READY","operator_review_required":True,"write_allowed":False}
f=out/f"{ts}_CHEROKEE_WW601_MULTISOURCE_CONTENT_PREVIEW.json";f.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("M99 v0.6.7.3 - EVIDENCE-BASED MULTI-SOURCE MULTILINGUAL CONTENT ENGINE")
print("HTTP policy: GET ONLY");print("Canonical identity:",c["identity_status"]);print("Stenso classification:",market["classification"])
print("Stenso description blocks detected:",market["description_blocks_detected"]);print("Market language signals:",market["market_language_signals"])
print("Supplier description use: FACT EXTRACTION + MARKET ADAPTATION");print("Supplier verbatim copy: BLOCKED");print("Unverified price/stock: BLOCKED")
print("Languages:",", ".join(docs));print("BG sites: BG + EN + RU");print("RO sites: RO + EN");print("Claim-level provenance: READY")
print("AI evidence contract: READY");print("OPERATOR REVIEW REQUIRED: YES");print("WRITE ALLOWED: NO");print("Output:",f)
