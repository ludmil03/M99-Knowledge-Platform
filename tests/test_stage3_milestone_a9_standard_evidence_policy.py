from app.services.standard_evidence_policy import *

def E(v,s): return StandardEvidence(v,s)

def test_supplier_evidence_preferred():
 r=resolve_standard(StandardApplicability.REQUIRED,[E("EN ISO 20345:2022+A1:2024",StandardEvidenceSource.SUPPLIER)])
 assert r.publish_gate_pass and r.provenance is StandardEvidenceSource.SUPPLIER

def test_manufacturer_closes_required_when_supplier_missing():
 r=resolve_standard(StandardApplicability.REQUIRED,[E("EN ISO 20345:2022+A1:2024",StandardEvidenceSource.MANUFACTURER)])
 assert r.publish_gate_pass and r.provenance is StandardEvidenceSource.MANUFACTURER

def test_authorized_evidence_fallback():
 r=resolve_standard(StandardApplicability.REQUIRED,[E("EN 343",StandardEvidenceSource.AUTHORIZED)])
 assert r.publish_gate_pass and r.provenance is StandardEvidenceSource.AUTHORIZED

def test_required_missing_blocks():
 r=resolve_standard(StandardApplicability.REQUIRED,[])
 assert not r.publish_gate_pass and r.blockers==("TECHNICAL_STANDARD_REQUIRED_NOT_PROVEN",)

def test_not_applicable_missing_does_not_block():
 r=resolve_standard(StandardApplicability.NOT_APPLICABLE,[])
 assert r.publish_gate_pass and r.status=="NOT_APPLICABLE" and not r.blockers

def test_unknown_missing_requires_review_not_invention():
 r=resolve_standard(StandardApplicability.UNKNOWN,[])
 assert not r.publish_gate_pass and r.standard is None
 assert "TECHNICAL_STANDARD_APPLICABILITY_REVIEW" in r.blockers

def test_conflicting_sources_block():
 r=resolve_standard(StandardApplicability.REQUIRED,[
  E("EN ISO 20345:2022+A1:2024",StandardEvidenceSource.SUPPLIER),
  E("EN ISO 20345:2022",StandardEvidenceSource.MANUFACTURER)])
 assert not r.publish_gate_pass and r.status=="CONFLICT"
 assert r.blockers==("TECHNICAL_STANDARD_CONFLICT",)

def test_equivalent_formatting_not_conflict():
 r=resolve_standard(StandardApplicability.REQUIRED,[
  E("EN ISO:20345:2022+A1:2024",StandardEvidenceSource.SUPPLIER),
  E("EN ISO 20345:2022+A1:2024",StandardEvidenceSource.MANUFACTURER)])
 assert r.publish_gate_pass and r.provenance is StandardEvidenceSource.SUPPLIER

def test_no_write_in_any_decision():
 for a in StandardApplicability:
  assert resolve_standard(a,[]).write_performed is False
