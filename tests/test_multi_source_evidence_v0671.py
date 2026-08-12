import unittest
from core.multi_source_evidence_v0671 import resolve,commercial
class T(unittest.TestCase):
 def test_manufacturer(self): self.assertEqual(resolve(["Cotton"],["cotton"])["status"],"VERIFIED")
 def test_conflict(self): self.assertEqual(resolve(["Cotton"],["Polyester"])["status"],"SOURCE_CONFLICT")
 def test_consensus(self): self.assertEqual(resolve([],["Regular","regular"])["status"],"SUPPLIER_CONSENSUS")
 def test_price_separation(self): self.assertIsNone(commercial("S","u",99,"BGN")["m99_selling_price"])
