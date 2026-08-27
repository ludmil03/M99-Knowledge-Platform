from __future__ import annotations
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.m99_phase45.common import Report
from scripts.m99_phase45 import stenso_live, local_persistence
from scripts.m99_phase45.prestashop_operator_gate import run as run_m99eu
from scripts.m99_phase45.dolibarr_live import run as run_dolibarr

STATE_FILE = Path.home() / "Desktop" / "M99_V073_PHASE45_OPERATOR_PRODUCT.json"
REPORT_FILE = Path.home() / "Desktop" / "M99_V073_PHASE45_GUI_REAL_TEST_REPORT.json"

def _report_run(fn, *args):
    r = Report(REPORT_FILE)
    fn(r, *args)
    r.save()
    return [x.__dict__ for x in r.checks]

def run_local_persistence():
    return _report_run(local_persistence.run, REPO_ROOT)

def run_stenso():
    return _report_run(
        stenso_live.run,
        os.getenv("STENSO_CATEGORY_URL", stenso_live.DEFAULT_CATEGORY),
        os.getenv("STENSO_PRODUCT_URL", stenso_live.DEFAULT_PRODUCT),
    )

def run_m99eu_test(api_key: str, base_url: str, category_id: str):
    if not api_key:
        raise ValueError("PrestaShop API key is required")
    return _report_run(run_m99eu, base_url.strip() or "https://m99.eu", api_key.strip(), category_id.strip() or "26")

def run_dolibarr_test(api_key: str, base_url: str):
    if not api_key or not base_url:
        raise ValueError("Dolibarr TEST URL and API key are required")
    return _report_run(run_dolibarr, base_url.strip(), api_key.strip())

def operator_state() -> dict[str, Any] | None:
    if not STATE_FILE.exists():
        return None
    return json.loads(STATE_FILE.read_text(encoding="utf-8"))

def operator_decide(decision: str, notes: str, actor: str):
    data = operator_state()
    if not data:
        raise ValueError("No operator-review product exists")
    if data.get("operator_status") != "PENDING_REVIEW":
        raise ValueError(f"Product state is {data.get('operator_status')}, not PENDING_REVIEW")

    decision = decision.upper()
    if decision not in {"APPROVE", "REJECT"}:
        raise ValueError("Unsupported operator decision")

    data["operator_reviewed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S%z")
    data["operator_actor"] = actor
    data["operator_notes"] = notes
    if decision == "APPROVE":
        data["operator_status"] = "APPROVED"
        data["daily_sync_status"] = "READY_FOR_BASELINE"
        data["delete_status"] = "KEEP_PRODUCT"
    else:
        data["operator_status"] = "REJECTED"
        data["daily_sync_status"] = "BLOCKED"
        data["delete_status"] = "OPERATOR_DECISION_FIX_OR_DELETE"

    STATE_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

def dashboard():
    state = operator_state()
    return {
        "state": state,
        "report_path": str(REPORT_FILE),
        "state_path": str(STATE_FILE),
        "stenso_url": os.getenv("STENSO_PRODUCT_URL", stenso_live.DEFAULT_PRODUCT),
        "m99eu_default_url": os.getenv("M99EU_BASE_URL", "https://m99.eu"),
        "m99eu_default_category": os.getenv("M99EU_TEST_CATEGORY_ID", "26"),
        "dolibarr_default_url": os.getenv("DOLIBARR_BASE_URL", ""),
    }
