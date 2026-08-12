import unittest
from core.robust_supplier_discovery_v067112 import relevant,merge
class T(unittest.TestCase):
 def test_wwe(self):self.assertTrue(relevant("Cherokee WWE601"))
 def test_ww(self):self.assertTrue(relevant("Cherokee WW601"))
 def test_other(self):self.assertFalse(relevant("Cherokee WWE620"))
 def test_merge(self):
  a={"supplier":"Stenso","pages":[]};b={"supplier":"Palltex","pages":[]};self.assertIsNone(merge(a,b)["policy"]["m99_selling_price"])
