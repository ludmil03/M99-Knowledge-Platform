# R3.6.1E — Calenda GET Color Variant + Per-Variant Image Hydration Fix

Live diagnostic evidence for Calenda 31809 established:
- visible 20 / БЯЛ -> GET color=7
- visible 26 / черно -> GET color=206
- visible 42 / тъмно-синьо -> GET color=211
- visible 46 / небесно-синьо -> GET color=231

R3.6.1E parses the exact textile GET forms, preserves both the visible color code and supplier source_variant_id, then performs a read-only GET for every variant URL and records that response's product image as the variant's image evidence.

Generic legacy variant discovery remains fallback-only when textile forms are absent.

No Identity/DRAFT activation, DB migration, Calenda write, m99.eu write, stock write, commit or push.
