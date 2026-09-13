
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.canonical_identity_allocator import M99_RE

def test_m99_identity_regex():
    assert M99_RE.fullmatch("M99-1")
    assert M99_RE.fullmatch("M99-999999")
    assert not M99_RE.fullmatch("93300")
    assert not M99_RE.fullmatch("65-014-0")
    assert not M99_RE.fullmatch("blue")

def test_allocator_source_never_promotes_supplier_or_mpn():
    s=(ROOT/"admin-platform/app/services/v073_phase46/canonical_identity_allocator.py").read_text(encoding="utf-8")
    assert 'kwargs["m99_reference"]=ref' in s
    assert 'supplier_ref=_text(getattr(item,"supplier_reference",""))' in s
    assert 'm99_reference"]=supplier_ref' not in s
    assert 'manufacturer' not in s.lower() or 'Manufacturer MPN are never used' in s
