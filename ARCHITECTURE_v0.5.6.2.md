# v0.5.6.2 — Bultex Live Launcher Fix

Fixes the Windows launcher failure:

`ModuleNotFoundError: No module named 'integrations'`

## Cause
The live test script was started in a context where Python treated `scripts/`
as the import root. Therefore the repository root containing `integrations/`
was not guaranteed to be available on `sys.path`.

## Fix
- `RUN_BULTEX_LIVE_READ.bat` resolves and changes to the repository root.
- PowerShell runner explicitly sets the repository root in `PYTHONPATH`.
- Live test is started as a module:
  `py -3 -m scripts.test_bultex_live_read`
- `scripts/__init__.py` makes operational scripts an explicit package.
- Regression tests verify launcher behavior.

Credential behavior is unchanged:
credentials exist only in the current PowerShell process and are cleared after
the test.

No Dolibarr, basket, order or website write capability is added.
