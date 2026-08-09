import unittest
from core.identity_v2 import format_m99_id,validate_m99_id,ChannelIdentity
class T(unittest.TestCase):
 def test_format(self):
  self.assertEqual(format_m99_id(1),"M99 000001")
  self.assertTrue(validate_m99_id("M99 000001"))
  self.assertFalse(validate_m99_id("M99-PV-000001"))
 def test_url_protected(self):
  c=ChannelIdentity("CH-MELA99","2045",canonical_url="https://x/old")
  self.assertTrue(c.validate_update({"canonical_url":"https://x/new","external_product_id":"2045"}))
