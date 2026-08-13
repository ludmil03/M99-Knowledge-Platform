import unittest
from core.central_secrets_v067451 import validate_fields,redacted_status
class T(unittest.TestCase):
 def test_missing(self):
  self.assertEqual(validate_fields({"api_key":""},["api_key"]),["api_key"])
 def test_redaction(self):
  self.assertEqual(redacted_status({"api_key":"SECRET"},["api_key"])["api_key"],"***REDACTED***")
 def test_complete(self):
  self.assertEqual(validate_fields({"username":"u","app_password":"p"},["username","app_password"]),[])
