from core.multisource_content_engine_v0673 import evidence_model,preview,deterministic_preview
m=evidence_model([{"field":"canonical_style","value":"WW601","content_use":"ALLOW"}],{"market_language_signals":[]})
assert set(preview(m))=={"bg","en","ru","ro"}
assert preview(m)==deterministic_preview(m)
print("M99 v0.6.7.3.2 - PREVIEW API COMPATIBILITY SMOKE CHECK")
print("preview import: OK")
print("deterministic_preview alias: OK")
print("COMPATIBILITY: PASS")
