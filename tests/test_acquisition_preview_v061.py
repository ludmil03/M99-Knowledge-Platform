import unittest
from pathlib import Path
from core.acquisition_preview import build_preview_from_file, normalize_m99_id, AcquisitionValidationError

class T(unittest.TestCase):
    def setUp(self):
        self.source=Path("tests/fixtures/product_acquisition_sample.json")
        self.channels=Path("config/channels/channel_rules_v0.6.0.json")

    def test_preview_is_read_only(self):
        p=build_preview_from_file(self.source,self.channels)
        self.assertEqual(p["mode"],"PREVIEW_ONLY")
        self.assertFalse(p["writes"]["dolibarr"])
        self.assertFalse(p["writes"]["channels"])

    def test_draft_and_url_keep(self):
        p=build_preview_from_file(self.source,self.channels)
        self.assertEqual(p["productgroup"]["lifecycle"],"draft")
        mela=next(x for x in p["channel_preview"] if x["channel"]=="mela99.com")
        self.assertEqual(mela["url_action"],"KEEP")

    def test_medical_site_blocked_for_nonmedical(self):
        p=build_preview_from_file(self.source,self.channels)
        channels={x["channel"] for x in p["channel_preview"]}
        self.assertNotIn("medicinski-drehi.com",channels)

    def test_operator_review(self):
        p=build_preview_from_file(self.source,self.channels)
        self.assertTrue(p["review"]["operator_required"])
        self.assertIsNone(p["review"]["decision"])

    def test_m99_format(self):
        self.assertEqual(normalize_m99_id("M99 100001"),"M99 100001")
        with self.assertRaises(AcquisitionValidationError):
            normalize_m99_id("M99-100001")
