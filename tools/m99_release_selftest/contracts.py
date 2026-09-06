from __future__ import annotations

import re
from pathlib import Path

FORBIDDEN_REPO_PARTS = {
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "backups",
}
FORBIDDEN_SUFFIXES = {".bak", ".zip", ".pem", ".pfx", ".key"}
SECRET_PATTERNS = (
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----", re.I),
    re.compile(
        r"(?i)(api[_-]?key|access[_-]?token|client[_-]?secret|password)"
        r"\s*[:=]\s*['\"][^'\"]{8,}['\"]"
    ),
)


def assert_safe_payload_paths(paths: list[str]) -> None:
    for raw in paths:
        normalized = raw.replace("\\", "/")
        p = Path(normalized)
        if any(part in FORBIDDEN_REPO_PARTS for part in p.parts):
            raise AssertionError(f"Forbidden runtime/cache path: {normalized}")
        if p.suffix.lower() in FORBIDDEN_SUFFIXES:
            raise AssertionError(f"Forbidden payload suffix: {normalized}")
        if normalized == "admin-platform/data/m99_admin.db":
            raise AssertionError("Operational Admin DB must never be a release payload.")


def assert_no_literal_secrets(text: str) -> None:
    for pattern in SECRET_PATTERNS:
        if pattern.search(text):
            raise AssertionError("Secret-like literal detected.")


def assert_exact_allowlist(actual: list[str], expected: list[str]) -> None:
    a = sorted(x.replace("\\", "/") for x in actual)
    e = sorted(x.replace("\\", "/") for x in expected)
    if a != e:
        raise AssertionError(f"Allowlist mismatch: expected={e!r}, actual={a!r}")
