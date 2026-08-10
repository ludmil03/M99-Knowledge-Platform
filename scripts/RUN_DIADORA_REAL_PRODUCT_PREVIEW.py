from pathlib import Path
import json
from core.acquisition_preview import build_preview_from_file
from core.product_evidence import EvidenceRecord, evidence_bundle

SOURCE=Path("tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json")
CHANNELS=Path("config/channels/channel_rules_v0.6.0.json")
OUTPUT=Path("output/diadora_glove_abox_low_pro_s1ps_preview.json")

data=json.loads(SOURCE.read_text(encoding="utf-8"))
manufacturer=EvidenceRecord(**data["manufacturer_evidence"])
supplier_candidates=[EvidenceRecord(**x) for x in data.get("supplier_candidates",[])]

preview=build_preview_from_file(SOURCE,CHANNELS)
preview["evidence"]=evidence_bundle(manufacturer,supplier_candidates)
preview["source_product"]={
    "manufacturer_item":manufacturer.facts.get("manufacturer_item"),
    "protection_class":manufacturer.facts.get("protection_class"),
    "colour":manufacturer.facts.get("colour"),
    "eu_sizes":manufacturer.facts.get("eu_sizes",[]),
}
preview["review"]["blocking_flags"]=[]
for candidate in preview["evidence"]["supplier_candidates"]:
    cmp=candidate["comparison"]
    if cmp["decision"]=="REVIEW":
        preview["review"]["blocking_flags"].extend(cmp["reasons"])
preview["review"]["blocking_flags"]=sorted(set(preview["review"]["blocking_flags"]))

OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.write_text(json.dumps(preview,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

print("M99 Real Product Evidence Preview v0.6.2")
print("========================================")
print("Product:",preview["productgroup"]["name"])
print("M99 ID:",preview["productgroup"]["m99_id"])
print("Manufacturer item:",preview["source_product"]["manufacturer_item"])
print("Protection class:",preview["source_product"]["protection_class"])
print("EU variants:",len(preview["variants"]))
print("Eligible channels:",len(preview["channel_preview"]))
print("Supplier candidate checks:")
for x in preview["evidence"]["supplier_candidates"]:
    c=x["comparison"]
    print(" -",x["supplier"],"=>",c["decision"],"|",",".join(c["reasons"]) or "OK")
print("Blocking review flags:",preview["review"]["blocking_flags"] or "NONE")
print("Writes to Dolibarr: NO")
print("Writes to websites: NO")
print("Preview written to:",OUTPUT)
