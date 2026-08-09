import unittest
from unittest.mock import Mock, patch

from integrations.bultex_b2b.safe_live_auth import BultexSafeReadOnlyClient


LOGIN = """
<form name="flog" method="get" action="/pap/login.php" onsubmit="return checkit()">
<input name="act" type="text">
<input name="CNum" type="text">
<input name="edaderpu_40796fd29e86fb53477225cf4f9f2eb8" type="text">
<input name="edaderpp_a087f91fb4f3c5843203b08487c91d76" type="text">
</form>
"""


class SafeLiveAuthTests(unittest.TestCase):

    @patch("integrations.bultex_b2b.safe_live_auth.requests.Session.get")
    def test_dynamic_fields_are_discovered(self, get):
        r = Mock()
        r.text = LOGIN
        r.url = "https://b2b.bultex99.com:8823/pap/login.php"
        r.status_code = 200
        r.raise_for_status = Mock()
        get.return_value = r

        c = BultexSafeReadOnlyClient()
        f = c.discover_login_form()

        self.assertEqual(f.method, "get")
        self.assertEqual(f.client_code_field, "CNum")
        self.assertTrue(f.username_field.startswith("edaderpu_"))
        self.assertTrue(f.password_field.startswith("edaderpp_"))
        self.assertEqual(f.action_value, "li")

    def test_product_endpoint_rejects_non_numeric_ids(self):
        c = BultexSafeReadOnlyClient()
        with self.assertRaises(ValueError):
            c.read_product("../order", "222", "Radinovo")
