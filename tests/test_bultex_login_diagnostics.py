import unittest
from unittest.mock import Mock, patch

from integrations.bultex_b2b.login_diagnostics import diagnose_login_page


HTML_NO_STANDARD_PASSWORD = """
<html>
<body>
<form method="post" action="/pap/login.php" onsubmit="return doLogin();">
  <input type="text" name="CNum" value="secret-client">
  <input type="text" name="UName">
  <input type="text" name="PwdField">
  <input type="hidden" name="act" value="login">
</form>
<script src="/common.js"></script>
<script>
function doLogin() { return true; }
</script>
<div>Клиентски код</div>
<div>Потребителско име</div>
<div>Парола</div>
<div>Вход</div>
</body>
</html>
"""


class BultexLoginDiagnosticsTests(unittest.TestCase):

    @patch("integrations.bultex_b2b.login_diagnostics.requests.Session.get")
    def test_diagnostics_do_not_require_password_input_type(self, get):
        r = Mock()
        r.text = HTML_NO_STANDARD_PASSWORD
        r.status_code = 200
        r.url = "https://b2b.bultex99.com:8823/pap/login.php?CNum=secret-client"
        r.raise_for_status = Mock()
        get.return_value = r

        d = diagnose_login_page(client_code_hint="secret-client")

        self.assertEqual(d.status_code, 200)
        self.assertTrue(d.password_keyword_present)
        self.assertTrue(d.login_keyword_present)
        self.assertEqual(len(d.forms), 1)
        self.assertEqual(d.forms[0].method, "post")
        self.assertIn("CNum", [x.name for x in d.forms[0].inputs])
        self.assertIn("doLogin", d.inline_function_names)

    @patch("integrations.bultex_b2b.login_diagnostics.requests.Session.get")
    def test_final_url_redacts_query_values(self, get):
        r = Mock()
        r.text = "<html></html>"
        r.status_code = 200
        r.url = "https://b2b.bultex99.com:8823/pap/login.php?CNum=TOPSECRET"
        r.raise_for_status = Mock()
        get.return_value = r

        d = diagnose_login_page(client_code_hint="TOPSECRET")

        self.assertNotIn("TOPSECRET", d.final_url)
        self.assertIn("CNum=<redacted>", d.final_url)
