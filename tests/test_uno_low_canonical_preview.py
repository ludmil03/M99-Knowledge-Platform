from integrations.bultex99_supplier.uno_low_canonical_preview import *
def test_four_languages(): assert tuple(build_preview().content)==("bg","en","ru","ro")
def test_fail_closed_identity():
 assert quality_gate(build_preview("NEW"))["pass"]
 assert not quality_gate(build_preview("AMBIGUOUS"))["pass"]
 assert not quality_gate(build_preview("UNRESOLVED"))["pass"]
def test_evidence():
 e={x.field:x.value for x in build_preview().evidence}
 assert e["model"]=="11720E" and e["standard"]=="EN ISO 20345:2022+A1:2024"
 assert e["protection_class"]=="S3S FO LG SR ESD" and e["sizes"]=="36-48"
def test_price_policy(): assert allowed_price_range()==("57.90","58.31")
def test_no_write(): assert build_preview().write_performed is False
def test_next_gate(): assert quality_gate(build_preview())["next_gate"]=="CHANNEL_PREFLIGHT_AND_OPERATOR_WRITE_APPROVAL"
