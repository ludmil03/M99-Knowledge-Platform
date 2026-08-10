import json
import unittest
from pathlib import Path

from core.existing_product_discovery import (
    DiscoveryEvidence,
    evaluate_channel_discovery,
    evaluate_discovery,
)
from core.content_seo_preview import (
    build_diadora_content_preview,
)


class ExistingProductDiscoveryContentSeoV063Tests(unittest.TestCase):

    def setUp(self):
        self.product = json.loads(
            Path(
                "tests/fixtures/"
                "diadora_glove_abox_low_pro_s1ps_real.json"
            ).read_text(encoding="utf-8")
        )
        self.facts = self.product[
            "manufacturer_evidence"
        ]["facts"]

    def test_public_search_miss_requires_review(self):
        r = DiscoveryEvidence(
            channel="mela99.com",
            query_type="manufacturer_item",
            query_value="701.183121_80013",
            result="NO_PUBLIC_EXACT_MATCH_FOUND",
        )
        result = evaluate_channel_discovery([r])
        self.assertEqual(
            result["status"],
            "NO_PUBLIC_EXACT_MATCH_FOUND_REVIEW_REQUIRED",
        )
        self.assertFalse(
            result["first_publish_allowed"]
        )
        self.assertTrue(
            result["operator_confirmation_required"]
        )

    def test_exact_existing_match_preserves_identity(self):
        r = DiscoveryEvidence(
            channel="mela99.com",
            query_type="manufacturer_item",
            query_value="701.183121_80013",
            result="EXACT_MATCH",
            matched_url="/existing-diadora-product",
            matched_product_id="1234",
        )
        result = evaluate_channel_discovery([r])
        self.assertEqual(
            result["status"], "EXACT_MATCH_FOUND"
        )
        self.assertTrue(
            result["preserve_existing_url"]
        )
        self.assertTrue(
            result["preserve_existing_product_id"]
        )

    def test_content_exists_for_four_eligible_channels(self):
        c = build_diadora_content_preview(
            self.facts
        )
        self.assertEqual(
            set(c.keys()),
            {
                "mela99.com",
                "m99.eu",
                "rabotni-drehi.com",
                "laviro.ro",
            },
        )

    def test_required_languages_exist(self):
        c = build_diadora_content_preview(
            self.facts
        )
        self.assertEqual(
            set(c["mela99.com"].keys()),
            {"bg", "en"},
        )
        self.assertEqual(
            set(c["m99.eu"].keys()),
            {"bg", "en"},
        )
        self.assertEqual(
            set(c["rabotni-drehi.com"].keys()),
            {"bg"},
        )
        self.assertEqual(
            set(c["laviro.ro"].keys()),
            {"ro"},
        )

    def test_channel_copy_is_not_verbatim_duplicate(self):
        c = build_diadora_content_preview(
            self.facts
        )
        self.assertNotEqual(
            c["mela99.com"]["bg"]["long_description"],
            c["rabotni-drehi.com"]["bg"]["long_description"],
        )
        self.assertNotEqual(
            c["mela99.com"]["en"]["long_description"],
            c["m99.eu"]["en"]["long_description"],
        )

    def test_near_match_supplier_facts_are_not_used_in_content(self):
        c = build_diadora_content_preview(
            self.facts
        )
        serialized = json.dumps(
            c, ensure_ascii=False
        )
        self.assertNotIn("152.4", serialized)
        self.assertNotIn("298.07", serialized)
        self.assertNotIn("S3S", serialized)

    def test_content_uses_exact_s1ps_identity(self):
        c = build_diadora_content_preview(
            self.facts
        )
        serialized = json.dumps(
            c, ensure_ascii=False
        )
        self.assertIn("S1PS", serialized)
        self.assertIn("35–48", serialized)


if __name__ == "__main__":
    unittest.main()
