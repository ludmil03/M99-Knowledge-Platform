from __future__ import annotations
import re

GATE_ID="R7K.3_PUBLISH_READY_CONTENT_GATE"
_HTML_RE=re.compile(r"<\s*(?:br|p|div|span|script|style)\b|<[^>]+>",re.I)

TYPE_RULES={
 "trousers": {
   "source": ("панталон","trouser","trousers","pants","брюк","брюки"),
   "forbidden": ("мъжка риза","дамска риза"," риза ","shirt","рубашк"),
 },
 "shirt": {
   "source": ("риза","shirt","рубашк"),
   "forbidden": ("панталон","trouser","trousers","брюк","брюки"),
 },
}

def _text(v)->str:return str(v or "").strip()
def _flat(doc:dict)->str:
    vals=[doc.get("product_name"),doc.get("h1"),doc.get("short_description"),doc.get("long_description_html"),doc.get("meta_title"),doc.get("meta_description")]
    return " ".join(_text(x) for x in vals).lower()

def infer_source_type(*values)->str:
    text=" ".join(_text(v).lower() for v in values)
    for kind,rule in TYPE_RULES.items():
        if any(tok in text for tok in rule["source"]):return kind
    return "unknown"

def validate_publish_ready_content(*,supplier_title:str,supplier_description:str,languages:dict)->dict:
    blockers=[]
    source_type=infer_source_type(supplier_title,supplier_description)
    for code,doc in (languages or {}).items():
        if not isinstance(doc,dict):
            blockers.append(f"{code}: content document has invalid structure.");continue
        flat=_flat(doc)
        for field in ("product_name","h1","meta_title","meta_description","short_description"):
            val=_text(doc.get(field))
            if _HTML_RE.search(val):blockers.append(f"{code}: raw HTML is not allowed in {field}.")
        if source_type in TYPE_RULES:
            bad=[x for x in TYPE_RULES[source_type]["forbidden"] if x in flat]
            if bad:blockers.append(f"{code}: product-type mismatch; source is {source_type} but content contains {', '.join(sorted(set(bad)))}.")
    return {"gate_id":GATE_ID,"source_type":source_type,"pass":not blockers,"blockers":blockers}
