from __future__ import annotations
import json
import os
import sys
import time
import uuid
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any

@dataclass
class Check:
    name: str
    status: str
    detail: str
    data: dict[str, Any] | None = None

class Report:
    def __init__(self, path: Path):
        self.path = path
        self.checks: list[Check] = []

    def add(self, name: str, status: str, detail: str, data: dict[str, Any] | None = None):
        c = Check(name=name, status=status, detail=detail, data=data)
        self.checks.append(c)
        print(f"[{status}] {name}: {detail}", flush=True)

    def save(self):
        payload = {
            "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "checks": [asdict(x) for x in self.checks],
            "summary": {
                "PASS": sum(x.status == "PASS" for x in self.checks),
                "FAIL": sum(x.status == "FAIL" for x in self.checks),
                "SKIP": sum(x.status == "SKIP" for x in self.checks),
            },
        }
        self.path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    @property
    def failed(self):
        return any(x.status == "FAIL" for x in self.checks)

def env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()

def test_ref(prefix="M99-P45") -> str:
    return f"{prefix}-{time.strftime('%Y%m%d-%H%M%S')}-{uuid.uuid4().hex[:6].upper()}"

def require_requests():
    try:
        import requests
        return requests
    except Exception as exc:
        raise RuntimeError(f"requests unavailable: {exc}") from exc

def safe_text(response, limit=1000):
    try:
        return response.text[:limit]
    except Exception:
        return "<unavailable>"
