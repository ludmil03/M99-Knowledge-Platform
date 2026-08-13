from core.cherokee_canonical_merge_v0672 import compare_fact, build_canonical

print("M99 v0.6.7.3.1 - COMPATIBILITY SMOKE CHECK")
print("compare_fact import: OK")
print("build_canonical import: OK")
print("consensus status:", compare_fact("material", "Cotton", "cotton")["status"])
print("COMPATIBILITY: PASS")
