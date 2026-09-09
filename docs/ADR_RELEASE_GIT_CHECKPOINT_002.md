# RELEASE-GIT-002 — Accepted milestone must receive a Git checkpoint

Status: DECIDED

Required sequence:
1. internal self-test;
2. Windows/runtime acceptance;
3. exact governed-change audit;
4. maintained regression;
5. credentials/secrets guard;
6. git diff --cached --check;
7. commit with milestone identifier;
8. push;
9. verify HEAD == origin/main;
10. record commit SHA in README/current-state documentation.

Do not click "Commit all changed files" blindly. Runtime sidecars, DB files,
backups, caches and temporary/output evidence are not automatically source code.

If acceptance fails, rollback first and DO NOT create a checkpoint commit.
