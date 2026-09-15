from tools.safe_git_checkpoint_engine import classify

def test_runtime(): assert classify("var/phase46_draft_enrichment/job-27.json")=="DENY"
def test_env(): assert classify(".env")=="DENY"
def test_source(): assert classify("admin-platform/app/main.py")=="ALLOW"
def test_unknown(): assert classify("mystery.bin")=="REVIEW"
