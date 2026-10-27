from dataclasses import asdict
from app.services.stage5_live_ui_readiness import from_preflight
def build_live_preflight_view(result):
 x=from_preflight(result);return {**asdict(x),'credential':'PRESENT_NOT_PRINTED','publish_enabled':False,'write_allowed':False,'write_performed':False}
