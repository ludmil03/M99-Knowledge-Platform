import json, unittest
from pathlib import Path
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from core.content_seo_preview import build_diadora_content_preview
from core.content_quality_guard import evaluate_all_content, evaluate_content_quality
from core.claim_traceability import build_claim_trace

class T(unittest.TestCase):
    def setUp(self):
        src=json.loads(Path("tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json").read_text(encoding="utf-8"))
        m=src["manufacturer_evidence"]
        self.c=build_canonical_product_facts(m["source_name"],m["source_url"],m["facts"])
        self.f=canonical_values(self.c)
        self.content=build_diadora_content_preview(self.f)

    def test_no_double_s1ps(self):
        self.assertNotIn("S1PS S1PS",json.dumps(self.content,ensure_ascii=False))

    def test_no_unsupported_textile_claim(self):
        s=json.dumps(self.content,ensure_ascii=False).lower()
        self.assertNotIn("текстилна защита от пробиване",s)
        self.assertNotIn("textile anti-puncture",s)

    def test_bg_language_guard(self):
        s=json.dumps(self.content["mela99.com"]["bg"],ensure_ascii=False).lower()
        self.assertNotIn("nitrile rubber",s)
        self.assertNotIn("exact item",s)

    def test_ro_language_guard(self):
        s=json.dumps(self.content["laviro.ro"]["ro"],ensure_ascii=False).lower()
        self.assertNotIn("nitrile rubber",s)
        self.assertNotIn("aluminium 200j",s)

    def test_all_docs_content_ready(self):
        q=evaluate_all_content(self.content,self.f)
        self.assertEqual(q["status"],"CONTENT_READY")
        self.assertEqual(len(q["results"]),6)
        self.assertTrue(all(x["issues"]==[] for x in q["results"]))

    def test_specs_exist(self):
        for langs in self.content.values():
            for c in langs.values():
                self.assertTrue(c["specifications"])

    def test_claim_trace(self):
        t=build_claim_trace(self.c)
        self.assertGreaterEqual(len(t),15)
        self.assertTrue(all(x["status"]=="SUPPORTED" for x in t))

    def test_guard_rejects_double_s1ps(self):
        bad=dict(self.content["mela99.com"]["en"])
        bad["seo_title"]="Diadora GLOVE A.BOX LOW PRO S1PS S1PS Safety Shoes"
        q=evaluate_content_quality("mela99.com","en",bad,self.f)
        self.assertIn("DUPLICATE_PROTECTION_CLASS",q["issues"])

    def test_guard_rejects_unsupported_claim(self):
        bad=dict(self.content["mela99.com"]["bg"])
        bad["short_description"] += " Текстилна защита от пробиване."
        q=evaluate_content_quality("mela99.com","bg",bad,self.f)
        self.assertEqual(q["status"],"REVIEW")
        self.assertTrue(any(x.startswith("UNSUPPORTED_CLAIM:") for x in q["issues"]))

if __name__=="__main__":
    unittest.main()
