from .channel_registry import CHANNELS
from .adapter_contracts import contracts
def build(reference="M99 100018"):
 c=contracts();return {"reference":reference,"write_allowed":False,"channels":[{"channel_id":x["channel_id"],"platform":x["platform"],"version":x["version"],"role":x["role"],**c[x["channel_id"]]} for x in CHANNELS]}
