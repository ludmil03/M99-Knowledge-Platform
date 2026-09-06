# R3.6.1E2 — Future Import Cleanup Fix

R3.6.1E1 compile passed but import-time test collection failed because the generated connector still contained:

    import annotations

after the correct line:

    from __future__ import annotations

That normal import is invalid because `annotations` is a future feature, not an importable module.

R3.6.1E2 removes only the stray normal import and enforces:
1. exactly one `from __future__ import annotations`;
2. exactly one `import html as html_lib`;
3. no `import annotations`.

All R3.6.1E Calenda GET color mapping and per-variant image hydration logic is preserved unchanged.

No Identity/DRAFT activation, DB migration, Calenda write, m99.eu write, stock write, commit or push.
