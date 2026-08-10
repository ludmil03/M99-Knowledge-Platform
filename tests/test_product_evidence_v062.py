import json, unittest
from pathlib import Path
from core.product_evidence import EvidenceRecord, compare_supplier_candidate

class T(unittest.TestCase):
    def setUp(self):
        data=json.loads(Path("tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json").read_text(encoding="utf-8"))
        self.m=EvidenceRecord(**data["manufacturer_evidence"])
        self.s=EvidenceRecord(**data["supplier_candidates"][0])

    def test_manufacturer_exact_item_is_s1ps(self):
        self.assertEqual(self.m.facts["manufacturer_item"],"701.183121_80013")
        self.assertEqual(self.m.facts["protection_class"],"S1PS")

    def test_real_fixture_has_fourteen_eu_variants(self):
        data=json.loads(Path("tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json").read_text(encoding="utf-8"))
        self.assertEqual(len(data["variants"]),14)

    def test_supplier_near_match_is_not_auto_merged(self):
        result=compare_supplier_candidate(self.m,self.s)
        self.assertFalse(result["auto_merge_allowed"])
        self.assertEqual(result["decision"],"REVIEW")
        self.assertIn("PROTECTION_CLASS_CONFLICT",result["reasons"])

    def test_no_exact_supplier_manufacturer_item_match(self):
        result=compare_supplier_candidate(self.m,self.s)
        self.assertFalse(result["exact_manufacturer_item_match"])
        self.assertIn("NO_EXACT_MANUFACTURER_ITEM_MATCH",result["reasons"])
