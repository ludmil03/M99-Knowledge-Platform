import pytest
from integrations.m99eu_prestashop.live_write_transport import *
def test_host_and_method_failclosed():
 with pytest.raises(WriteViolation):OneShotPS9WriteTransport("http://m99.eu","x")
 t=OneShotPS9WriteTransport("https://m99.eu","secret")
 with pytest.raises(WriteViolation):t.request_once("DELETE","/api/products/1")
