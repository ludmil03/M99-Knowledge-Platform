# M99 R4.3.3 — Windows Accepted Runtime Baseline

Windows acceptance date: 2026-09-23.
Observed result: M99 Knowledge Control Center successfully opened at `/r43/control-center`.
Visible navigation: Control Center, Product Publish Center, Diagnostics, Updates.
Publish panel confirms existing R4.1/R4.1.1 publish/recovery engine is preserved.

Runtime identity rule: on Windows a venv launcher command may execute through the base Python executable.
Identity therefore requires the exact M99 venv launcher in CommandLine plus uvicorn, app.main:app,
host 127.0.0.1 and port 8070; ExecutablePath equality with the venv launcher is not required.

Safety: foreign/unverified listeners are never killed. Runtime bootstrap performs no product-site write,
DB migration, commit, or push.
