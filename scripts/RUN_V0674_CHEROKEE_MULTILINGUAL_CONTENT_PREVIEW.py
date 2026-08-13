from pathlib import Path
import json
from datetime import datetime,timezone
from core.cherokee_multilingual_content_v0674 import build_preview
d=build_preview();ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ");o=Path("output/v0674_cherokee_multilingual_content");o.mkdir(parents=True,exist_ok=True);f=o/f"{ts}_CHEROKEE_WW601_FULL_MULTILINGUAL_CANONICAL_CONTENT_PREVIEW.json";f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
print("M99 v0.6.7.4 - CHEROKEE WW601 FULL MULTILINGUAL CANONICAL CONTENT PREVIEW")
print("WRITE ALLOWED: NO")
print("Languages: BG EN RU RO")
for s,l in d["channel_language_policy"].items(): print(s,"=>",",".join(x.upper() for x in l))
for l,x in d["documents"].items(): print(l.upper(),"=> H1 YES | H2",len(x["h2"]),"| FAQ",x["faq_count"],"| supplier verbatim copy NO")
print("M99 selling price: NOT SELECTED");print("Stock: NOT CLAIMED");print("Output:",f)
