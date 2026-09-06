from __future__ import annotations

import pytest

from tools.m99_release_selftest.contracts import (
    assert_exact_allowlist,
    assert_no_literal_secrets,
    assert_safe_payload_paths,
)


def test_release_selftest_accepts_safe_paths():
    assert_safe_payload_paths([
        "admin-platform/app/routers/r37_add_products_flow.py",
        "tests/test_example.py",
        "ARCHITECTURE_example.md",
    ])


@pytest.mark.parametrize(
    "path",
    [
        "admin-platform/data/m99_admin.db",
        "admin-platform/data/backups/x.db",
        "x/.venv/a.py",
        "x/__pycache__/a.pyc",
        "temp.bak",
        "installer.zip",
        "secret.pem",
    ],
)
def test_release_selftest_rejects_unsafe_paths(path):
    with pytest.raises(AssertionError):
        assert_safe_payload_paths([path])


def test_release_selftest_secret_guard():
    assert_no_literal_secrets('api_key = os.getenv("M99EU_API_KEY")')
    synthetic_secret = "1" * 32
    with pytest.raises(AssertionError):
        assert_no_literal_secrets('api_key = "' + synthetic_secret + '"')


def test_release_selftest_exact_allowlist():
    assert_exact_allowlist(["a.py", "b.md"], ["b.md", "a.py"])
    with pytest.raises(AssertionError):
        assert_exact_allowlist(["a.py", "oops.db"], ["a.py"])
