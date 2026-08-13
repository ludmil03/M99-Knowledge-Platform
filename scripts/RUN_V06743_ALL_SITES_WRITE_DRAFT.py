from __future__ import annotations
import os,sys,json
from pathlib import Path
from core.cherokee_all_sites_publish_v06743 import build_all_sites_package

CONFIRM="WRITE_DRAFT ALL_SITES CHEROKEE WW601 M99"

def main():
 d=build_all_sites_package()
 blocked=[s for s,m in d["publication_manifest"].items() if m["adapter_status"]!="READY_BY_PLATFORM"]
 if blocked:
  print("ALL-SITES WRITE BLOCKED")
  print("Missing/unknown channel adapters:",blocked)
  print("Policy: partial publication is forbidden.")
  print("Configure these adapters before ALL_SITES WRITE_DRAFT.")
  return 2

 if not d["similarity_guard"]["all_pass"]:
  print("ALL-SITES WRITE BLOCKED: channel duplication guard failed")
  return 3

 print("ALL SITES ARE CONFIGURED FOR CONTROLLED WRITE_DRAFT")
 print("This command would create/update DRAFT/INACTIVE content only.")
 print("Type exactly:",CONFIRM)
 confirmation=input("Confirmation: ").strip()
 if confirmation!=CONFIRM:
  print("Exact confirmation required.")
  return 4

 # Deliberately no transport mutation in v0.6.7.4.3 until every adapter is proven.
 print("TRANSPORT WRITE BLOCKED IN v0.6.7.4.3")
 print("Reason: all six channel adapters must be proven with per-channel readback/rollback before first real mutation.")
 print("Next gate: v0.6.7.4.4 ALL-SITES ADAPTER VALIDATION + READBACK.")
 return 5

if __name__=="__main__":
 raise SystemExit(main())
