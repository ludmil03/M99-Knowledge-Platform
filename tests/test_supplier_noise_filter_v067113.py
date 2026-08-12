import unittest
from core.supplier_noise_filter_v067113 import canonical_url,page_type,classify
class TestV067113(unittest.TestCase):
    def test_fragment(self): self.assertEqual(canonical_url("https://stenso.net/x#product-details"),"https://stenso.net/x")
    def test_image(self): self.assertEqual(page_type("https://stenso.net/a-wwe601.jpg"),"IMAGE_ASSET")
    def test_search_block(self): self.assertFalse(classify("https://stenso.net/product?s=Cherokee+WWE601","","Cherokee WWE601 navy")["commercial_allowed"])
    def test_exact(self): self.assertTrue(classify("https://stenso.net/produkt/cherokee-navy-wwe601","Cherokee Navy WWE601","")["commercial_allowed"])
    def test_wrong_colour(self): self.assertEqual(classify("https://stenso.net/produkt/cherokee-grey-wwe601","Cherokee Grey WWE601","")["evidence_role"],"SAME_MODEL_WRONG_COLOUR")
