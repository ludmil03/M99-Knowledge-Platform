import unittest
from integrations.bultex_b2b.login_js_diagnostics import _extract_function_body

class T(unittest.TestCase):
    def test_extract(self):
        s='function checkit(){ var a=document.forms[0].CNum.value; if(!a){return false;} return true;}'
        b=_extract_function_body(s,"checkit")
        self.assertIn("CNum",b)
        self.assertIn("return true",b)
