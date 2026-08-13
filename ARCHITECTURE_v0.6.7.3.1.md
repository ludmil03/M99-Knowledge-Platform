# M99 v0.6.7.3.1 — Compatibility & Installer Hotfix

Purpose:
- Restore the public v0.6.7.2 API required by existing tests.
- Keep v0.6.7.3 as an additive content layer.
- Never commit when any test fails.
- Keep the console open on failure.
- Perform no website write.

Backward-compatible functions restored:
- compare_fact()
- build_canonical()

The hotfix does not publish products and does not assign M99 price/reference automatically.
