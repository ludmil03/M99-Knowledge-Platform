# R3.6.1A — Regex Variant Capture Fix

R3.6.1 failed its dedicated live-control test because the generated Python regex patterns
contained double-escaped backslashes, so `\d` was interpreted as a literal backslash+d
instead of a digit class.

R3.6.1A fixes only that implementation defect and strengthens the dedicated tests.
No runtime write path is enabled. Calenda access remains read-only.
