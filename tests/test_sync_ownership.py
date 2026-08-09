import unittest
from core.sync_ownership import can_write
class T(unittest.TestCase):
 def test_stock(self):
  self.assertTrue(can_write("stock","DOLIBARR"))
  self.assertFalse(can_write("stock","M99"))
 def test_url(self):
  self.assertFalse(can_write("canonical_url","M99"))
