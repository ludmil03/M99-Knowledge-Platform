import unittest
from core.multisource_content_engine_v0673 import evidence_model,preview
class T(unittest.TestCase):
 def m(self):
  return evidence_model([{"field":"canonical_style","value":"WW601","source":"Cherokee Uniforms","content_use":"ALLOW"}],
  {"market_language_signals":["медицинска туника"],"description_blocks_detected":1})
 def test_original(self): self.assertTrue(self.m()["rules"]["original_m99_content"])
 def test_no_copy(self): self.assertFalse(self.m()["rules"]["supplier_verbatim_copy"])
 def test_price(self): self.assertFalse(self.m()["rules"]["price_in_content"])
 def test_stock(self): self.assertFalse(self.m()["rules"]["unverified_stock_in_content"])
 def test_languages(self): self.assertEqual(set(preview(self.m())),{"bg","en","ru","ro"})
 def test_structure(self): self.assertEqual(preview(self.m())["bg"]["faq_count"],6)
 def test_provenance(self): self.assertTrue(self.m()["rules"]["claim_level_provenance"])
