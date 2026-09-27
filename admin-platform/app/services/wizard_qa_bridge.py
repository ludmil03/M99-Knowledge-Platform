from __future__ import annotations
from dataclasses import dataclass
from app.services.unified_qa_readiness import UnifiedQAResult

@dataclass(frozen=True)
class WizardQAView:
    status:str
    blockers:tuple[str,...]
    ready_for_targets:bool
    publish_enabled:bool=False
    write_performed:bool=False

def build_wizard_qa_view(qa:UnifiedQAResult)->WizardQAView:
    status="READY_FOR_TARGETS" if qa.ready_for_targets else "BLOCKED"
    return WizardQAView(status=status,blockers=qa.blockers,
                        ready_for_targets=qa.ready_for_targets,
                        publish_enabled=False,write_performed=False)
