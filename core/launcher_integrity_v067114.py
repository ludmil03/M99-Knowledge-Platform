from pathlib import Path

RECENT_BAT = [
    "RUN_V0670_CHEROKEE_WW601_DISCOVERY_PREVIEW_WITH_KEY.bat",
    "RUN_V0671_SUPPLIER_INTELLIGENCE_PREVIEW.bat",
    "RUN_V06711_SUPPLIER_PAGE_EXTRACTION_PREVIEW.bat",
    "RUN_V067112_ROBUST_SUPPLIER_DISCOVERY_PREVIEW.bat",
    "RUN_V067113_SUPPLIER_NOISE_FILTER_PREVIEW.bat",
]
RECENT_PS1 = [
    "run_v0670_cherokee_ww601_discovery_preview.ps1",
    "run_v0671_supplier_intelligence_preview.ps1",
    "run_v06711_supplier_page_extraction_preview.ps1",
    "run_v067112_robust_supplier_discovery_preview.ps1",
    "run_v067113_supplier_noise_filter_preview.ps1",
]

def contains_literal_newline_escape(text):
    return "\\n" in text or "\\r\\n" in text

def validate_launcher_text(text, kind):
    errors=[]
    if contains_literal_newline_escape(text):
        errors.append("LITERAL_NEWLINE_ESCAPE_FOUND")
    if kind=="bat":
        if "@echo off" not in text.lower(): errors.append("BAT_MISSING_ECHO_OFF")
        if "powershell.exe" not in text.lower(): errors.append("BAT_MISSING_POWERSHELL")
    if kind=="ps1":
        if "Set-Location" not in text: errors.append("PS1_MISSING_SET_LOCATION")
        if "PYTHONPATH" not in text: errors.append("PS1_MISSING_PYTHONPATH")
    return errors

def scan_repo_launchers(repo):
    scripts=repo/"scripts"; results={}
    for name in RECENT_BAT:
        p=scripts/name
        if p.exists():
            results[name]=validate_launcher_text(p.read_text(encoding="utf-8",errors="replace"),"bat")
    for name in RECENT_PS1:
        p=scripts/name
        if p.exists():
            results[name]=validate_launcher_text(p.read_text(encoding="utf-8-sig",errors="replace"),"ps1")
    return results

def all_ok(results):
    return all(not x for x in results.values())
