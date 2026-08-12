import unittest
from core.launcher_integrity_v067114 import contains_literal_newline_escape, validate_launcher_text

class T(unittest.TestCase):
    def test_literal_escape(self):
        self.assertTrue(contains_literal_newline_escape("@echo off\\r\\npause\\r\\n"))
    def test_real_newlines(self):
        self.assertFalse(contains_literal_newline_escape("@echo off\r\npause\r\n"))
    def test_good_bat(self):
        self.assertEqual(validate_launcher_text('@echo off\r\npowershell.exe -File "x.ps1"\r\n',"bat"),[])
    def test_good_ps1(self):
        self.assertEqual(validate_launcher_text('$Repo="C:\\\\x"\nSet-Location $Repo\n$env:PYTHONPATH=$Repo\n',"ps1"),[])
    def test_bad_ps1(self):
        self.assertIn("PS1_MISSING_PYTHONPATH",validate_launcher_text('Set-Location "C:\\\\x"\n',"ps1"))
