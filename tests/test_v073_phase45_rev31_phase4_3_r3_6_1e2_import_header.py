from pathlib import Path

def test_calenda_connector_import_header_is_valid():
    path = Path("admin-platform/app/services/v073_phase45/calenda_public_connector.py")
    lines = path.read_text(encoding="utf-8").splitlines()
    assert lines[0] == "from __future__ import annotations"
    assert "import html as html_lib" in lines[:6]
    assert "import annotations" not in lines
    assert lines.count("from __future__ import annotations") == 1
