from types import SimpleNamespace
from app.services.stage4_ui_authorization_bridge import *
def D(ref='5161',source='БУЛТЕКС'):return SimpleNamespace(source_name=source,ready_targets=['m99.eu'],selection_mode='one_product',selected_product_refs=[ref])
def test_exact_scope_no_write():
 p=build_publish_preview(D(),None);assert len(p.scope_token)==64 and not p.publish_enabled and not p.write_performed and verify_preview_scope(p,p.scope_token)
def test_mutation_changes_scope():assert build_publish_preview(D('1'),None).scope_token!=build_publish_preview(D('2'),None).scope_token
def test_cyrillic_deterministic():assert build_publish_preview(D(source='Доставчик БГ'),None).scope_token==build_publish_preview(D(source='Доставчик БГ'),None).scope_token
