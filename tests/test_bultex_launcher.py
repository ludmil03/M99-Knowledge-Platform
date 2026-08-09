import unittest
from pathlib import Path


class BultexLauncherTests(unittest.TestCase):

    def test_live_runner_sets_repo_root_and_pythonpath(self):
        path = Path("scripts/run_bultex_live_read.ps1")
        text = path.read_text(encoding="utf-8-sig")

        self.assertIn("$RepoRoot", text)
        self.assertIn("Set-Location $RepoRoot", text)
        self.assertIn("$env:PYTHONPATH", text)
        self.assertIn("py -3 -m scripts.test_bultex_live_read", text)

    def test_bat_launcher_changes_to_repo_root(self):
        path = Path("scripts/RUN_BULTEX_LIVE_READ.bat")
        text = path.read_text(encoding="ascii")

        self.assertIn("REPO_ROOT", text)
        self.assertIn('cd /d "%REPO_ROOT%"', text)
