from pathlib import Path
from datetime import datetime,timezone
import json
from core.cherokee_full_content_v06742 import build
d=build();ts=datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ");o=Path("output/v06742_cherokee_full_content");o.mkdir(parents=True,exist_ok=True);f=o/f"{ts}_CHEROKEE_WW601_FULL_CONTENT_PREVIEW.json";f.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding="utf-8")
print("M99 v0.6.7.4.2 - CHEROKEE WW601 FULL CONTENT PREVIEW");print("WRITE ALLOWED: NO")
for site,langs in d["documents"].items():
 for lang,x in langs.items():print(f"{site} {lang.upper()} | H1=YES H2={len(x['sections'])} H3/FAQ={len(x['faq'])} HTML={len(x['long_description_html'])} ALT={len(x['image_alt'])} SCORE={x['quality_score']}")
print("Price: NOT SELECTED");print("Stock: NOT CLAIMED");print("Output:",f)
