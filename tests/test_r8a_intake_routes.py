"""Exercise selection through HTTP and verify the real application route graph."""
from collections import Counter
import json
import os
from pathlib import Path
import secrets
import subprocess
import sys

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "admin-platform") not in sys.path:
    sys.path.insert(0, str(ROOT / "admin-platform"))

from app.core.db import get_db
from app.routers import unified_add_products as intake
from app.services.v073_phase45.unified_add_products import SourceView


@pytest.fixture
def selection_client(monkeypatch):
    source = SourceView("approved-source", "SUPPLIER", "Palltex", "palltex.bg",
                        "https://palltex.bg/", "ACTIVE")
    monkeypatch.setattr(intake, "_selected_source_context", lambda *_: (source, None, []))
    monkeypatch.setattr(intake, "approved_sources", lambda _: [source])
    monkeypatch.setattr(intake, "approved_categories", lambda _: [])
    app = FastAPI()
    app.include_router(intake.router)
    app.dependency_overrides[get_db] = lambda: None
    with TestClient(app) as client:
        yield client


def test_selection_http_accepts_exact_product(selection_client):
    response = selection_client.post("/add-products/selection", data={
        "source_uuid": "approved-source", "selection_mode": "ONE_PRODUCT",
        "selected_url": "https://palltex.bg/product/123",
        "requested_target": "m99.eu",
    })
    assert response.status_code == 200
    assert response.context["selection_review"]["selected_urls"] == [
        "https://palltex.bg/product/123"]
    assert response.context["selection_review"]["requested_targets"] == ["m99.eu"]
    assert response.context["selection_review"]["write_performed"] is False
    assert response.context["selection_review"]["publish_enabled"] is False


def test_selection_http_deduplicates_without_expanding_scope(selection_client):
    response = selection_client.post("/add-products/selection", data={
        "source_uuid": "approved-source", "selection_mode": "MULTIPLE_PRODUCTS",
        "selected_url": ["https://palltex.bg/product/123"] * 2,
        "requested_target": ["m99.eu", "m99.eu"],
    })
    assert response.status_code == 200
    review = response.context["selection_review"]
    assert review["selected_urls"] == ["https://palltex.bg/product/123"]
    assert review["requested_targets"] == ["m99.eu"]
    assert review["publish_enabled"] is False


@pytest.mark.parametrize("mode,urls", [
    ("ONE_PRODUCT", []),
    ("ONE_PRODUCT", ["https://palltex.bg/product/1", "https://palltex.bg/product/2"]),
    ("MULTIPLE_PRODUCTS", ["https://unapproved.example/product/1"]),
    ("INVALID_MODE", ["https://palltex.bg/product/1"]),
])
def test_selection_http_rejects_invalid_input(selection_client, mode, urls):
    response = selection_client.post("/add-products/selection", data={
        "source_uuid": "approved-source", "selection_mode": mode,
        "selected_url": urls, "requested_target": "m99.eu",
    })
    assert response.status_code == 400
    assert response.context["selection_review"] is None
    assert response.context["error"]


def test_actual_publish_center_routes_registered_once():
    root = Path(__file__).resolve().parents[1]
    env = dict(os.environ, M99_SESSION_SECRET=secrets.token_hex(32),
               M99_DATABASE_URL="sqlite:///:memory:",
               PYTHONPATH=os.pathsep.join((str(root), str(root / "admin-platform"))))
    script = """
import json
from app.main import app
print(json.dumps([(sorted(r.methods), r.path) for r in app.routes
                  if hasattr(r, 'methods') and r.path.startswith('/r730/publish-center')]))
"""
    result = subprocess.run([sys.executable, "-c", script], cwd=root / "admin-platform",
                            env=env, capture_output=True, text=True, check=True)
    routes = json.loads(result.stdout.strip().splitlines()[-1])
    counts = Counter((tuple(methods), path) for methods, path in routes)
    expected = {
        (("GET",), "/r730/publish-center"),
        (("POST",), "/r730/publish-center/preflight"),
        (("POST",), "/r730/publish-center/publish"),
        (("GET",), "/r730/publish-center/recovery"),
    }
    assert set(counts) == expected
    assert all(count == 1 for count in counts.values())
