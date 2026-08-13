import unittest
from core.cherokee_multilingual_content_v0674 import build_preview
class T(unittest.TestCase):
 def setUp(self): self.d=build_preview()
 def test_no_write(self): self.assertFalse(self.d["write_allowed"])
 def test_languages(self): self.assertEqual(set(self.d["documents"]),{"bg","en","ru","ro"})
 def test_bg_channels(self):
  for s in ["mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com"]: self.assertEqual(self.d["channel_language_policy"][s],["bg","en","ru"])
 def test_ro_channels(self):
  for s in ["laviro.ro","alviro.ro"]: self.assertEqual(self.d["channel_language_policy"][s],["ro","en"])
 def test_structure(self):
  for x in self.d["documents"].values(): self.assertTrue(x["h1"]);self.assertGreaterEqual(len(x["h2"]),6);self.assertEqual(x["faq_count"],6)
 def test_price(self): self.assertIsNone(self.d["commercial"]["m99_selling_price"])
 def test_stock(self): self.assertIsNone(self.d["commercial"]["stock_claim"])
 def test_copy_guard(self): self.assertFalse(self.d["guards"]["supplier_verbatim_copy"])
 def test_provenance(self): self.assertTrue(self.d["guards"]["claim_level_provenance"])
 def test_identity(self): self.assertEqual(self.d["identity"]["style"],"WW601")
