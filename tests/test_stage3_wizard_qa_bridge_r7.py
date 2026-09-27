from app.services.unified_qa_readiness import UnifiedQAResult
from app.services.wizard_qa_bridge import build_wizard_qa_view
def test_ready_qa_is_display_only():
 v=build_wizard_qa_view(UnifiedQAResult((),True))
 assert v.status=="READY_FOR_TARGETS" and v.ready_for_targets
 assert not v.publish_enabled and not v.write_performed
def test_blockers_are_preserved_for_operator_ui():
 v=build_wizard_qa_view(UnifiedQAResult(("VAT_NOT_PROVEN","CONTENT_NOT_READY"),False))
 assert v.status=="BLOCKED" and v.blockers==("VAT_NOT_PROVEN","CONTENT_NOT_READY")
def test_bridge_has_no_publish_authorization():
 assert build_wizard_qa_view(UnifiedQAResult((),True)).publish_enabled is False
