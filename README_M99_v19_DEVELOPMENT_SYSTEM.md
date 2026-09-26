# M99 Development System v19.3 — MAXSIM
README v17 is enforced by RUN_M99_RELEASE_GATE.cmd and M99_AGENT_CONTRACT.yaml.

v19.3 replaces fragile patching with one centralized build_stage_plan. This directly fixes the v19.2 defect where a corrected full_regression function existed but the old naked-pytest lambda remained wired into execution.

FULL_REGRESSION is explicit allow-list only:
1. repository tests/ with repository cwd;
2. admin-platform/tests/ with admin-platform cwd.

output/, hotfix backups, scripts/, network diagnostics and credential-dependent probes are never implicit pytest regression roots.

No website write, DB migration, process kill, reset, clean, rebase, force push, or automatic merge is permitted by this release gate.
