from pathlib import Path
import os
from app.services.v073_phase46 import durable_draft_enrichment as d

def test_atomic_roundtrip(tmp_path,monkeypatch):
 monkeypatch.setenv("M99_PHASE46_DRAFT_STORE",str(tmp_path))
 c={"target":"m99eu","languages":["EN","BG","RU"],"documents":{"EN":{},"BG":{},"RU":{}}}
 r=d.save(job_id=10,item_id=7,supplier_reference="93100",manufacturer_evidence={"status":"OPERATOR_CONFIRMED_EXACT"},content_bundle=c,target="m99eu")
 assert r["persisted"] and d.load(10)["supplier_reference"]=="93100"
 assert not list(tmp_path.glob("*.tmp"))

def test_tamper_blocked(tmp_path,monkeypatch):
 monkeypatch.setenv("M99_PHASE46_DRAFT_STORE",str(tmp_path))
 c={"target":"m99eu","languages":["EN","BG","RU"],"documents":{"EN":{},"BG":{},"RU":{}}}
 d.save(job_id=10,item_id=7,supplier_reference="93100",manufacturer_evidence={},content_bundle=c,target="m99eu")
 p=tmp_path/'job-10.json'; p.write_text(p.read_text().replace('93100','93101'))
 try:d.load(10);assert False
 except RuntimeError:pass

def test_missing_language_blocked(tmp_path,monkeypatch):
 monkeypatch.setenv("M99_PHASE46_DRAFT_STORE",str(tmp_path))
 try:d.save(job_id=1,item_id=1,supplier_reference='x',manufacturer_evidence={},content_bundle={"languages":["EN"],"documents":{"EN":{}}},target='m99eu');assert False
 except ValueError:pass


def test_r4_preserves_frozen_r3_no_mapped_carrier_contract():
    from pathlib import Path
    svc=Path("admin-platform/app/services/v073_phase46/content_manufacturer_intelligence.py").read_text(encoding="utf-8")
    assert 'LEGACY_NO_MAPPED_DRAFT_EVIDENCE_CARRIER="NO_MAPPED_DRAFT_EVIDENCE_CARRIER"' in svc
    assert 'result["legacy_schema_reason"]=LEGACY_NO_MAPPED_DRAFT_EVIDENCE_CARRIER' in svc
    assert 'result["persistence_upgrade"]="R4_DURABLE_DRAFT_SIDECAR"' in svc
