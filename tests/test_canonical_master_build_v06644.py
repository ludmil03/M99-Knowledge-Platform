import unittest
from core.canonical_master_build_v06644 import build_master_preview

def snap(ref,price,cats=2,imgs=9,combos=6):
    return {
        "scalar_fields":{"reference":ref,"price":price,"id_tax_rules_group":"1"},
        "associations":{
            "categories":[{"id":str(i)} for i in range(cats)],
            "images":[{"id":str(i)} for i in range(imgs)],
            "combinations":[{"id":str(i)} for i in range(combos)],
        }
    }

class T(unittest.TestCase):
    def test_no_write(self):
        r=build_master_preview(snap("MELA-REF","195"),snap("","292"),{"languages":{"bg_id":"2","en_id":"1"},"review_category":{"id":"93","active":False}})
        self.assertFalse(r["decision_gates"]["write_allowed"])
        self.assertIsNone(r["container"]["selected_product_id"])

    def test_reference_proposal_is_m99(self):
        r=build_master_preview(snap("MELA-REF","195"),snap("","292"),{"languages":{"bg_id":"2","en_id":"1"},"review_category":{"id":"93","active":False}})
        self.assertEqual(r["proposed_master"]["reference"]["proposed"],"M99 100017")
        self.assertIn("MELA-REF",r["proposed_master"]["reference"]["legacy_candidates"])

    def test_bg_en_content_distinct(self):
        r=build_master_preview(snap("MELA-REF","195"),snap("","292"),{"languages":{"bg_id":"2","en_id":"1"},"review_category":{"id":"93","active":False}})
        bg=r["proposed_master"]["content"]["bg"]["long_description_html"]
        en=r["proposed_master"]["content"]["en"]["long_description_html"]
        self.assertNotEqual(bg,en)
        self.assertIn("Често задавани въпроси",bg)
        self.assertIn("Frequently asked questions",en)

    def test_no_price_autoselection(self):
        r=build_master_preview(snap("MELA-REF","195"),snap("","292"),{"languages":{"bg_id":"2","en_id":"1"},"review_category":{"id":"93","active":False}})
        self.assertIsNone(r["proposed_master"]["commercial"]["price"]["proposed"])
