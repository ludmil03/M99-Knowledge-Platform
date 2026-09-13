from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[1];PATCH=ROOT/'scripts/phase46_r7c_patch_active_hydration.py'
def load():
 spec=importlib.util.spec_from_file_location('p',PATCH);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def test_patch_exact_anchor():
 m=load();text='from app.services.v073_phase45.calenda_public_connector import (\n    CalendaPublicConnector,\n    CalendaConnectorError,\n)\ndef x():\n    try:\n            return CalendaPublicConnector(source.base_url).get_product(product_url)\n    except Exception:\n        pass\n';out=m.patched_text(text);assert 'postprocess_calenda_hydrated(CalendaPublicConnector' in out
def test_unknown_shape_blocks():
 m=load();blocked=False
 try:m.patched_text('def x(): pass')
 except RuntimeError:blocked=True
 assert blocked
