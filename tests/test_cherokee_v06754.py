import unittest, os
from decimal import Decimal
from core.cherokee_real_publish_v0675 import calculate_bgn, load_existing_content, REQUIRED, SKIPPED
from pathlib import Path

class T(unittest.TestCase):
    def test_price(self):
        self.assertEqual(calculate_bgn(Decimal("25.20")), Decimal("48.65"))
    def test_five_targets(self):
        self.assertEqual(len(REQUIRED),5)
        self.assertNotIn("m99.eu",REQUIRED)
        self.assertEqual(SKIPPED,"m99.eu")
    def test_content_engine_restored(self):
        repo=Path(__file__).resolve().parents[1]
        x=load_existing_content(repo)
        self.assertIsNotNone(x["provider"])
        self.assertIn("cherokee_full_content_v06742",x["provider"])
        self.assertIsInstance(x["document"],dict)
    def test_content_languages(self):
        from core.cherokee_full_content_v06742 import build
        d=build()
        self.assertEqual(set(d["documents"]["mela99.com"]),{"bg","en","ru"})
        self.assertEqual(set(d["documents"]["laviro.ro"]),{"ro","en"})
