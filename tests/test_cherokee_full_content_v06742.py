import unittest
from core.cherokee_full_content_v06742 import build
class T(unittest.TestCase):
 def setUp(self):self.d=build()
 def test_no_write(self):self.assertFalse(self.d["write_allowed"])
 def test_channels(self):self.assertEqual(self.d["channel_language_policy"]["laviro.ro"],["ro","en"])
 def test_full(self):
  for langs in self.d["documents"].values():
   for x in langs.values():self.assertEqual(len(x["sections"]),6);self.assertEqual(len(x["faq"]),8);self.assertIn("<h3>",x["long_description_html"]);self.assertGreaterEqual(len(x["image_alt"]),5)
 def test_localization(self):self.assertIn("вискоза",self.d["documents"]["mela99.com"]["bg"]["long_description_html"])
 def test_commercial(self):self.assertIsNone(self.d["commercial"]["m99_selling_price"]);self.assertIsNone(self.d["commercial"]["stock_claim"])
 def test_guards(self):self.assertFalse(self.d["guards"]["supplier_verbatim_copy"]);self.assertTrue(self.d["guards"]["claim_level_provenance"])
