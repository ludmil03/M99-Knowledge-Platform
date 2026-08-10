import json
import re
import unittest
from pathlib import Path

from core.acquisition_preview import (
    build_preview_from_file,
)
from core.product_evidence import (
    EvidenceRecord,
    compare_supplier_candidate,
)


class IdentityReviewScopeV0621Tests(unittest.TestCase):
    def setUp(self):
        self.source = Path(
            "tests/fixtures/"
            "diadora_glove_abox_low_pro_s1ps_real.json"
        )
        self.channels = Path(
            "config/channels/channel_rules_v0.6.0.json"
        )
        self.data = json.loads(
            self.source.read_text(encoding="utf-8")
        )

    def test_schema_is_0621(self):
        p = build_preview_from_file(
            self.source, self.channels
        )
        self.assertEqual(
            p["schema_version"], "0.6.2.1"
        )

    def test_all_variant_ids_are_m99_space_digits_only(self):
        p = build_preview_from_file(
            self.source, self.channels
        )
        for variant in p["variants"]:
            self.assertRegex(
                variant["variant_id"],
                r"^M99 \d{6}$",
            )
            self.assertEqual(
                variant["parent_m99_id"],
                "M99 100002",
            )

    def test_variants_do_not_reuse_productgroup_id(self):
        p = build_preview_from_file(
            self.source, self.channels
        )
        ids = {
            x["variant_id"]
            for x in p["variants"]
        }
        self.assertNotIn(
            p["productgroup"]["m99_id"],
            ids,
        )

    def test_diadora_variant_range_is_100003_to_100016(self):
        p = build_preview_from_file(
            self.source, self.channels
        )
        self.assertEqual(
            p["variants"][0]["variant_id"],
            "M99 100003",
        )
        self.assertEqual(
            p["variants"][-1]["variant_id"],
            "M99 100016",
        )

    def test_near_match_commercial_data_is_quarantined(self):
        manufacturer = EvidenceRecord(
            **self.data["manufacturer_evidence"]
        )
        supplier = EvidenceRecord(
            **self.data["supplier_candidates"][0]
        )
        c = compare_supplier_candidate(
            manufacturer, supplier
        )
        self.assertFalse(
            c["commercial_data_usable"]
        )
        self.assertFalse(
            c["pricing_eligible"]
        )
        self.assertFalse(
            c["availability_eligible"]
        )
        self.assertEqual(
            c["decision"], "REVIEW"
        )

    def test_base_preview_has_no_product_blocking_flags(self):
        p = build_preview_from_file(
            self.source, self.channels
        )
        self.assertEqual(
            p["review"]["blocking_flags"],
            [],
        )


if __name__ == "__main__":
    unittest.main()
