from pathlib import Path
import os
from alembic import command
from alembic.config import Config
def main():
    repo=Path(__file__).resolve().parents[2]
    url=os.getenv("M99_ADMIN_DATABASE_URL","").strip()
    confirm=os.getenv("M99_PHASE4_MIGRATION_CONFIRM","").strip()
    if not url:
        print("STOP: M99_ADMIN_DATABASE_URL is not configured."); return 2
    if confirm!="APPLY_V073_PHASE4":
        print("STOP: set M99_PHASE4_MIGRATION_CONFIRM=APPLY_V073_PHASE4 after backup/review."); return 3
    ini=repo/"admin-platform"/"alembic.ini"
    if not ini.exists():
        print(f"STOP: Alembic config not found: {ini}"); return 4
    cfg=Config(str(ini)); cfg.set_main_option("sqlalchemy.url",url); command.upgrade(cfg,"v073_phase4")
    print("M99 v0.7.3 Phase 4 migration applied."); return 0
if __name__=="__main__": raise SystemExit(main())
