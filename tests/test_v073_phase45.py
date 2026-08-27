from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS.parent) not in sys.path:
    sys.path.insert(0, str(SCRIPTS.parent))

from scripts.m99_phase45.common import test_ref
from scripts.m99_phase45.prestashop_live import _product_xml
from scripts.m99_phase45.stenso_live import _extract_sizes
from lxml import html

def test_ref_is_unique_and_prefixed():
    a, b = test_ref(), test_ref()
    assert a.startswith("M99-P45-")
    assert a != b

def test_prestashop_payload_is_inactive_hidden_and_multilingual():
    root = ET.fromstring("<prestashop><product/></prestashop>")
    langs = [{"id":"1","iso":"en","name":"English"},{"id":"2","iso":"bg","name":"Български"},{"id":"3","iso":"ru","name":"Русский"}]
    xml = _product_xml(root, "M99-P45-X", "26", langs, "1.00").decode()
    assert "<active>0</active>" in xml
    assert "<visibility>none</visibility>" in xml
    assert xml.count("<language id=") >= 18
    assert "M99-P45-X" in xml

def test_stenso_size_parser_marks_disabled_semantics():
    doc = html.fromstring("""
    <div>
      <button class="size disabled">36</button>
      <button class="size out-of-stock">37</button>
      <button class="size">38</button>
    </div>
    """)
    sizes = {x["size"]:x for x in _extract_sizes(doc)}
    assert sizes["36"]["unavailable"] is True
    assert sizes["37"]["unavailable"] is True
    assert sizes["38"]["unavailable"] is False


def test_daily_sync_policy_separates_dynamic_and_content():
    from scripts.m99_phase45.daily_sync_foundation import diff
    changes=diff(
        {"price":"10","availability":True,"description":"old"},
        {"price":"11","availability":False,"description":"new"},
    )
    by={x["field"]:x for x in changes}
    assert by["price"]["policy"]=="AUTO_SYNC_CANDIDATE"
    assert by["availability"]["policy"]=="AUTO_SYNC_CANDIDATE"
    assert by["description"]["policy"]=="OPERATOR_REVIEW"

def test_operator_gate_module_has_no_success_delete_contract():
    from scripts.m99_phase45 import prestashop_operator_gate as m
    source=Path(m.__file__).read_text(encoding="utf-8")
    assert "PENDING_REVIEW" in source
    assert "no automatic DELETE" in source
    assert ".delete(" not in source.lower()
