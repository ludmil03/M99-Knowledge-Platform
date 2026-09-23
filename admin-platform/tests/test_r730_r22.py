import pytest
from app.services.v073_multichannel.channel_registry import CHANNELS,get
from app.services.v073_multichannel.adapter_contracts import contracts,blocked_write,WriteBlocked
from app.services.v073_multichannel.preflight import build
def test_8():assert len(CHANNELS)==8
def test_ids():assert [x["channel_id"] for x in CHANNELS]==["m99.eu","mela99.com","medicinski-drehi.com","rabotni-drehi.com","laviro.ro","alviro.ro","toplinka.com","dolibarr"]
def test_versions():assert get("m99.eu")["version"]=="9.1.5" and get("dolibarr")["version"]=="20.0.2"
def test_replaceable():assert all(x["replaceable_platform"] and x["replaceable_version"] for x in CHANNELS)
def test_readonly():assert build()["write_allowed"] is False and all(not x["mutation_allowed"] for x in contracts().values())
def test_block():
 with pytest.raises(WriteBlocked):blocked_write()
