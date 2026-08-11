import json
from pathlib import Path
from integrations.channel_publish import Mela99ClientConfig,ControlledMela99Publisher
from core.live_channel_metadata import parse_categories_xml
client=ControlledMela99Publisher(Mela99ClientConfig(base_url="https://mela99.com",api_key_env="M99_MELA99_API_KEY",timeout_seconds=30))
r=parse_categories_xml(client.get_resource_xml("categories",{"display":"full"}),"Test",allow_inactive_review_category=True)
o=Path("output/v066422_test_category_diagnostics.json"); o.parent.mkdir(parents=True,exist_ok=True); o.write_text(json.dumps(r,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
print("HTTP policy: GET ONLY")
print("Test ready:",r["ready"]); print("Test ID:",r["selected_category_id"]); print("Test active:",r["selected_category_active"]); print("Writes to websites: NO"); print("Output:",o)
