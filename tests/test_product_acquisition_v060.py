import json
import tempfile
import unittest
from pathlib import Path

from core.product_acquisition import ProductGroup, ProductGroupLifecycle
from core.channel_policy_v2 import ChannelPolicy
from core.channel_pricing_v2 import stenso_target_price


class ProductAcquisitionV060Tests(unittest.TestCase):
    def setUp(self):
        self.config = Path("config/channels/channel_rules_v0.6.0.json")
        self.policy = ChannelPolicy(self.config)

    def test_medical_routes_to_all_relevant_channels(self):
        channels = self.policy.eligible_channels({"medical"})
        self.assertIn("medicinski-drehi.com", channels)
        self.assertIn("rabotni-drehi.com", channels)
        self.assertIn("mela99.com", channels)
        self.assertIn("laviro.ro", channels)
        self.assertIn("alviro.ro", channels)

    def test_workwear_blocked_from_medical_only_site(self):
        self.assertFalse(self.policy.eligible("medicinski-drehi.com", {"workwear"}))
        self.assertTrue(self.policy.eligible("rabotni-drehi.com", {"workwear"}))

    def test_horeca_allowed_everywhere_except_medical_site(self):
        channels = self.policy.eligible_channels({"horeca"})
        self.assertNotIn("medicinski-drehi.com", channels)
        for ch in ("mela99.com","m99.eu","rabotni-drehi.com","laviro.ro","alviro.ro"):
            self.assertIn(ch, channels)

    def test_delete_requires_literal_DELETE(self):
        p = ProductGroup("M99 100001", "Test", "Test", {"workwear"})
        self.assertFalse(p.can_delete("delete"))
        self.assertTrue(p.can_delete("DELETE"))

    def test_lifecycle(self):
        p = ProductGroup("M99 100001", "Test", "Test", {"workwear"})
        p.transition(ProductGroupLifecycle.ACTIVE)
        p.transition(ProductGroupLifecycle.PAUSED)
        p.transition(ProductGroupLifecycle.RETIRED)
        self.assertEqual(p.lifecycle, ProductGroupLifecycle.RETIRED)

    def test_stenso_price_rule_and_floor(self):
        self.assertEqual(str(stenso_target_price("100", "80")), "98.50")
        self.assertEqual(str(stenso_target_price("100", "99")), "99.00")


if __name__ == "__main__":
    unittest.main()
