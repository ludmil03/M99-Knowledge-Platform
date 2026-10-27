import pytest
from types import SimpleNamespace
from app.services.stage5_final_ui_publish import FinalPublishBlocked, resolve_reference
def test_reference_validation_before_network():
 cfg=SimpleNamespace(base_url="https://m99.eu",api_key="0123456789abcdef",timeout_seconds=20)
 with pytest.raises(FinalPublishBlocked,match="REFERENCE_INVALID"):
  resolve_reference(cfg,"M99-100019")
