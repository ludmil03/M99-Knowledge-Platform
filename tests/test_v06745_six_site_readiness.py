import unittest
from core.six_site_readiness_v06745 import wp_headers
class T(unittest.TestCase):
 def test_basic_auth(self):
  self.assertTrue(wp_headers("u","p")["Authorization"].startswith("Basic "))
 def test_no_write_words_in_probe(self):
  import inspect,core.six_site_readiness_v06745 as m
  s=inspect.getsource(m)
  self.assertNotIn("requests.post(",s)
  self.assertNotIn("requests.put(",s)
  self.assertNotIn("requests.delete(",s)
