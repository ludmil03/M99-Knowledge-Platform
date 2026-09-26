import importlib.util,json,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
C=json.loads((ROOT/"M99_AGENT_CONTRACT.yaml").read_text(encoding="utf-8-sig"))
SPEC=importlib.util.spec_from_file_location("gate",ROOT/"scripts/m99_release_gate.py")
G=importlib.util.module_from_spec(SPEC); SPEC.loader.exec_module(G)

def test_chain_exact():
 assert C["release_sequence"]==G.SEQUENCE
 assert C["checkpoint_sequence"]==G.CHECKPOINT
def test_v17_normative(): assert C["normative_source"]=="README_M99_v17_FULL_VERIFICATION_RULE.md"
def test_missing_gate_status(): assert C["missing_gate_status"]=="NOT_RELEASEABLE"
def test_continuous_execution(): assert C["continuous_execution"]["do_not_wait_when_technical_step_determined"] is True
def test_git_forbidden(): assert set(C["git"]["forbidden_operations"])=={"reset","clean","rebase","force_push","automatic_merge"}
def test_stable_never_mutated(): assert C["git"]["stable_baseline_never_mutated"] is True
def test_failed_never_baseline(): assert C["git"]["failed_revision_never_baseline"] is True
def test_exact_staging(): assert C["git"]["exact_staging_only"] is True
def test_no_ambiguous_retry(): assert C["safety"]["ambiguous_write_auto_retry"] is False
def test_update_never_create(): assert C["safety"]["update_never_fallback_create"] is True
def test_live_write_auth(): assert C["safety"]["website_write_requires_explicit_authorization"] is True
def test_db_migration_auth(): assert C["safety"]["db_migration_requires_explicit_authorization"] is True
def test_process_kill_auth(): assert C["safety"]["process_kill_requires_explicit_authorization"] is True
def test_write_targets(): assert C["publishing"]["write_targets_rule"]=="REQUESTED ∩ AUTHORIZED ∩ READY"
def test_supplier_separation(): assert set(C["supplier_architecture"]["separate_adapters"])=={"PALLTEX","STENSO_LEGACY","BULTEX99"}
def test_state_clean(): assert G.classify(0,0,0)=="CLEAN"
def test_state_staged(): assert G.classify(3,0,0)=="READY"
def test_state_unstaged_block(): assert G.classify(0,1,0)=="BLOCK"
def test_state_untracked_block(): assert G.classify(0,0,1)=="BLOCK"
def test_state_wrong_branch_block(): assert G.classify(1,0,0,True,False)=="BLOCK"
def test_state_remote_moved_block(): assert G.classify(1,0,0,False,True)=="BLOCK"
def test_protected_branches(): assert {"main","master","recovery/c447e0d-clean-reconstruction"}<=G.PROTECTED_BRANCHES
def test_no_pause(): assert "pause" not in (ROOT/"RUN_M99_RELEASE_GATE.cmd").read_text(encoding="utf-8-sig").lower()
def test_stage_plan_wires_full_regression():
 plan=G.build_stage_plan(ROOT,C,"")
 assert [n for n,_ in plan]==["STATIC","SYNTAX_AST","KNOWN_DEFECT_REGRESSION","STATE_SIMULATIONS","SAFETY_FAIL_CLOSED","FOCUSED_TESTS","FULL_REGRESSION","PACKAGE_INTEGRITY"]
def test_stage_plan_has_one_full_regression():
 assert [n for n,_ in G.build_stage_plan(ROOT,C,"")].count("FULL_REGRESSION")==1
def test_no_naked_pytest_in_full_regression_source():
 import inspect
 src=inspect.getsource(G.full_regression_gate)
 assert "deterministic_regression_suites" in src
 assert '["-m","pytest","-q"]' not in src
def test_synthetic_discovery_root_only():
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);(r/"tests").mkdir();(r/"output/hotfix_backup/x/tests").mkdir(parents=True);(r/"scripts").mkdir()
  s=G.deterministic_regression_suites(r)
  assert [(x["name"],x["targets"]) for x in s]==[("ROOT_TESTS",["tests"])]
def test_synthetic_discovery_admin_context():
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);(r/"tests").mkdir();(r/"admin-platform/tests").mkdir(parents=True)
  s=G.deterministic_regression_suites(r)
  assert len(s)==2 and s[1]["cwd"]==r/"admin-platform" and s[1]["targets"]==["tests"]
def test_backup_never_discovered():
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);(r/"output/hotfix_backup/v/tests").mkdir(parents=True)
  assert G.deterministic_regression_suites(r)==[]
def test_scripts_never_discovered():
 with tempfile.TemporaryDirectory() as d:
  r=Path(d);(r/"scripts").mkdir()
  (r/"scripts/test_live.py").write_text("raise Exception()",encoding="utf-8")
  assert G.deterministic_regression_suites(r)==[]
def test_contract_forbids_naked_repo_pytest(): assert C["full_regression_policy"]["naked_repository_pytest_forbidden"] is True
def test_admin_context_contract(): assert C["full_regression_policy"]["admin_platform_import_context"]=="cwd=admin-platform"
def test_selection_modes():
 assert {"ONE_PRODUCT","MULTIPLE_PRODUCTS","ONE_CATEGORY","MULTIPLE_CATEGORIES","ALL_CATEGORIES","ONLY_NEW","FIRST_N","MANUAL_SELECTION"}<=set(C["publishing"]["selection_modes"])
