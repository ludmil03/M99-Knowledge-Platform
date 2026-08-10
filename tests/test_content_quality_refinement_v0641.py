import json, unittest
from pathlib import Path
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from core.content_claims import build_claim_policy
from core.content_seo_preview import build_diadora_content_preview
from core.content_quality_guard import evaluate_all_content, evaluate_content_quality
from core.claim_traceability import build_claim_trace
from core.channel_content_profiles import CHANNEL_CONTENT_PROFILES

class ContentQualityRefinementV0641Tests(unittest.TestCase):
    def setUp(self):
        src=json.loads(Path("tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json").read_text(encoding="utf-8")); m=src["manufacturer_evidence"]
        self.c=build_canonical_product_facts(m["source_name"],m["source_url"],m["facts"]); self.f=canonical_values(self.c); self.p=build_claim_policy(self.f); self.content=build_diadora_content_preview(self.f)
    def test_four_channel_profiles(self): self.assertEqual(set(CHANNEL_CONTENT_PROFILES),{"mela99.com","m99.eu","rabotni-drehi.com","laviro.ro"})
    def test_six_channel_language_documents(self): self.assertEqual(sum(len(v) for v in self.content.values()),6)
    def test_dynamic_faq_is_deeper(self):
        for langs in self.content.values():
            for doc in langs.values(): self.assertGreaterEqual(len(doc["faq"]),5)
    def test_all_content_ready(self): self.assertEqual(evaluate_all_content(self.content,self.f)["status"],"CONTENT_READY")
    def test_claim_types(self):
        trace=build_claim_trace(self.c,self.p); self.assertTrue(any(x["claim_type"]=="FACT" for x in trace)); self.assertTrue(any(x["claim_type"]=="DERIVED_SAFE_CLAIM" for x in trace))
    def test_derived_claims_have_sources(self):
        for x in self.p["derived_safe_claims"]: self.assertTrue(x["derived_from"])
    def test_comparative_claim_is_blocked(self):
        bad=dict(self.content["mela99.com"]["bg"]); bad["short_description"] += " По-леко от традиционните стоманени решения."
        q=evaluate_content_quality("mela99.com","bg",bad,self.f); self.assertTrue(any(x.startswith("MARKETING_CLAIM_REQUIRES_EVIDENCE") for x in q["issues"]))
    def test_channel_long_descriptions_are_distinct(self):
        docs=[self.content["mela99.com"]["bg"]["long_description"],self.content["m99.eu"]["bg"]["long_description"],self.content["rabotni-drehi.com"]["bg"]["long_description"]]
        self.assertEqual(len(set(docs)),3)
    def test_publication_stays_disabled(self): self.assertFalse(evaluate_all_content(self.content,self.f)["publication_enabled"])
if __name__=="__main__": unittest.main()
