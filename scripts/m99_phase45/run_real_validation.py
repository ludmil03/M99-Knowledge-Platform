from __future__ import annotations
import argparse
from pathlib import Path
from .common import Report, env
from . import stenso_live, local_persistence
from .prestashop_operator_gate import run as run_m99eu_operator_gate
from .dolibarr_live import run as run_dolibarr

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--report", required=True)
    ap.add_argument("--require-m99eu", action="store_true")
    ap.add_argument("--require-dolibarr", action="store_true")
    args = ap.parse_args()

    repo = Path(args.repo)
    report = Report(Path(args.report))

    local_persistence.run(report, repo)
    stenso_live.run(
        report,
        env("STENSO_CATEGORY_URL", stenso_live.DEFAULT_CATEGORY),
        env("STENSO_PRODUCT_URL", stenso_live.DEFAULT_PRODUCT),
    )

    run_m99eu_operator_gate(
        report,
        env("M99EU_BASE_URL", "https://m99.eu"),
        env("M99EU_API_KEY"),
        env("M99EU_TEST_CATEGORY_ID", "26"),
    )

    # Dolibarr remains a disposable CRUD test because it is explicitly a test environment.
    run_dolibarr(report, env("DOLIBARR_BASE_URL"), env("DOLIBARR_API_KEY"))

    if args.require_m99eu and any(x.status == "SKIP" and x.name.startswith("m99.eu") for x in report.checks):
        report.add("Phase 4.5 m99.eu required gate", "FAIL", "m99.eu credentials were not supplied")
    if args.require_dolibarr and any(x.status == "SKIP" and x.name.startswith("Dolibarr") for x in report.checks):
        report.add("Phase 4.5 Dolibarr required gate", "FAIL", "Dolibarr credentials were not supplied")

    report.save()
    print(f"\nReport: {report.path}")
    return 1 if report.failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
