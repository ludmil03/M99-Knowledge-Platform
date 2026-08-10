import unittest
from core.controlled_publish_policy import validate_publish_gates

BASE={"single_product_scope":True,"target_channel_is_mela99":True,
"content_ready":True,"internal_discovery_complete":True,
"operator_approved":False,"audit_enabled":True,"rollback_enabled":True,
"pricing_approved":False,"availability_approved":False}

class T(unittest.TestCase):
    def test_dry_run_no_operator_gate(self):
        self.assertNotIn("GATE_FAILED:operator_approved",
            validate_publish_gates(dict(BASE,publish_mode="DRY_RUN")))
    def test_write_draft_operator_gate_retained(self):
        self.assertIn("GATE_FAILED:operator_approved",
            validate_publish_gates(dict(BASE,publish_mode="WRITE_DRAFT")))
    def test_live_all_write_gates_retained(self):
        f=validate_publish_gates(dict(BASE,publish_mode="PUBLISH_LIVE"))
        self.assertIn("GATE_FAILED:operator_approved",f)
        self.assertIn("GATE_FAILED:pricing_approved",f)
        self.assertIn("GATE_FAILED:availability_approved",f)
