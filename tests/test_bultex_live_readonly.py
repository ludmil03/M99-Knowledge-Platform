import unittest
from unittest.mock import Mock, patch

from integrations.bultex_b2b.live_readonly import BultexReadOnlyClient


LOGIN_HTML = """
<html><body>
<form method="post" action="/pap/login.php">
  <input type="text" name="CNum">
  <input type="text" name="UserName">
  <input type="password" name="Password">
  <input type="hidden" name="act" value="login">
  <input type="submit" name="submit" value="Вход">
</form>
</body></html>
"""


class BultexLiveReadOnlyTests(unittest.TestCase):

    @patch("integrations.bultex_b2b.live_readonly.requests.Session.get")
    def test_login_discovery(self, get):
        response = Mock()
        response.text = LOGIN_HTML
        response.raise_for_status = Mock()
        get.return_value = response

        client = BultexReadOnlyClient()
        fields = client.discover_login_form()

        self.assertEqual(fields.method, "post")
        self.assertEqual(fields.client_code_field, "CNum")
        self.assertEqual(fields.username_field, "UserName")
        self.assertEqual(fields.password_field, "Password")

    def test_product_id_is_read_only_numeric(self):
        client = BultexReadOnlyClient()
        with self.assertRaises(ValueError):
            client.read_product("../basket", "222", "Rad")
