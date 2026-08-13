import json
from pathlib import Path
from core.real_all_sites_publisher_v06744 import run

cfg=Path("config/publish/v0.6.7.4.4_all_sites_real_write.json")
data=json.loads(cfg.read_text(encoding="utf-8"))
raise SystemExit(run(data))
