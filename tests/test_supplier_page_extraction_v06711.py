import unittest
from core.supplier_page_extraction_v06711 import (
    identity_score, classify_candidates, build_supplier_summary, merge_evidence
)

class T(unittest.TestCase):
    def rec(self, title="", ref="", price=None, stock=None):
        return {
            "title": title, "supplier_reference": ref, "price": price,
            "promo_price": None, "currency": "BGN", "availability": stock,
            "size_availability": [], "description": None, "technical_facts": {},
            "images": [], "raw_text_excerpt": title, "source_url": "https://x"
        }

    def test_exact_reference(self):
        r=self.rec("Cherokee scrub top WW601","CK-WW601--")
        self.assertEqual(identity_score(r)["class"],"EXACT")

    def test_strong_title(self):
        r=self.rec("Cherokee WW601 Women's Scrub Top","")
        self.assertEqual(identity_score(r)["class"],"VERY_STRONG")

    def test_near_match_commercial_quarantined(self):
        r=self.rec("WW601 scrub top","",99.0,"IN_STOCK")
        x=classify_candidates([r])[0]
        self.assertEqual(x["identity"]["class"],"NEAR_MATCH")
        self.assertTrue(x["commercial_quarantined"])

    def test_supplier_price_preserved_not_selected(self):
        r=self.rec("Cherokee WW601","CK-WW601",99.0,"IN_STOCK")
        x=classify_candidates([r])
        s=build_supplier_summary(x)
        self.assertEqual(s["all_prices"][0]["price"],99.0)
        self.assertIsNone(s["m99_selling_price_proposed"])

    def test_merge_keeps_supplier_separate(self):
        a=classify_candidates([self.rec("Cherokee WW601","CK-WW601",99.0)])
        b=classify_candidates([self.rec("Cherokee WW601","WW601",109.0)])
        m=merge_evidence(a,b)
        self.assertIn("Stenso",m["supplier_evidence"])
        self.assertIn("Palltex",m["supplier_evidence"])
        self.assertTrue(m["commercial_policy"]["preserve_per_supplier"])
