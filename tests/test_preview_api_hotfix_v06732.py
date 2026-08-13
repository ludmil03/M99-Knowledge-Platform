import unittest
from core.multisource_content_engine_v0673 import evidence_model,preview,deterministic_preview
class T(unittest.TestCase):
 def m(self): return evidence_model([{"field":"canonical_style","value":"WW601","content_use":"ALLOW"}],{"market_language_signals":[]})
 def test_preview(self): self.assertEqual(set(preview(self.m())),{"bg","en","ru","ro"})
 def test_alias(self): self.assertEqual(preview(self.m()),deterministic_preview(self.m()))
 def test_bg(self): self.assertEqual(preview(self.m())["bg"]["faq_count"],6)
 def test_copy(self): self.assertFalse(self.m()["rules"]["supplier_verbatim_copy"])
 def test_price(self): self.assertFalse(self.m()["rules"]["price_in_content"])
 def test_stock(self): self.assertFalse(self.m()["rules"]["unverified_stock_in_content"])
 def test_original(self): self.assertTrue(self.m()["rules"]["original_m99_content"])
 def test_provenance(self): self.assertTrue(self.m()["rules"]["claim_level_provenance"])
