import unittest
from integrations.bultex_b2b.auth_response_diagnostics import _visible_text

class T(unittest.TestCase):
    def test_visible_text(self):
        t=_visible_text("<script>x()</script><div>Грешен вход</div>")
        self.assertIn("Грешен вход",t)
        self.assertNotIn("x()",t)
