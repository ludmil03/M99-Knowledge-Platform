import unittest
from core.seo_guardrails import *
class T(unittest.TestCase):
 def setUp(self): self.b=BaselineAudit("CH-MELA99","MKT-BG","https://x/old")
 def test_keep_without_evidence(self):
  self.assertEqual(evaluate_candidate(self.b,{"description":"x"},[],["description"]).decision,OptimizationDecision.KEEP)
 def test_protected_url(self):
  r=evaluate_candidate(self.b,{"canonical_url":"https://x/new"},["audit"],["canonical_url"])
  self.assertEqual(r.decision,OptimizationDecision.KEEP)
 def test_enrich(self):
  self.assertEqual(evaluate_candidate(self.b,{"faq":["x"]},["gap"],["faq"]).decision,OptimizationDecision.ENRICH)
