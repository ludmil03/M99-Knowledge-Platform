import errno
import pytest
import integrations.m99eu_prestashop.connection_diagnostic as d
def report(dns="PASS",tcp="PASS",tls="PASS",root="PASS",api="HTTP_RESPONSE",auth="PASS",status=200):
 return {"steps":[
 {"name":"dns","state":dns},{"name":"tcp_443","state":tcp},{"name":"tls","state":tls},
 {"name":"https_get_public","state":root,"http_status":200},
 {"name":"https_get_public","state":api,"http_status":401},
 {"name":"https_get_auth","state":auth,"http_status":status}]}
@pytest.mark.parametrize("method",["POST","PUT","PATCH","DELETE"])
def test_source_contains_no_write_methods(method):
 import inspect
 assert f'conn.request("{method}"' not in inspect.getsource(d)
def test_classifications():
 assert d.classify(report(dns="FAIL"))=="DNS_FAILURE"
 assert d.classify(report(tcp="FAIL"))=="TCP_443_FAILURE"
 assert d.classify(report(tls="FAIL"))=="TLS_FAILURE"
 assert d.classify(report(root="FAIL"))=="PUBLIC_HTTPS_CONNECTION_FAILURE"
 assert d.classify(report(api="FAIL",auth="FAIL",status=None))=="API_CONNECTION_RESET_OR_TRANSPORT_FAILURE"
 assert d.classify(report(auth="HTTP_RESPONSE",status=401))=="API_AUTH_REJECTED"
 assert d.classify(report(auth="HTTP_RESPONSE",status=403))=="API_AUTH_REJECTED"
 assert d.classify(report(auth="PASS",status=200))=="AUTHENTICATED_API_HTTP_OK"
def test_winerror_10054_is_sanitized():
 e=ConnectionResetError(10054,"secret message")
 x=d.safe_error(e)
 assert "ConnectionResetError" in x and "10054" in x and "secret message" not in x
def test_bad_host_blocks():
 with pytest.raises(d.DiagnosticViolation):d.diagnose("https://example.com","X")
def test_no_key_in_report(monkeypatch):
 monkeypatch.setattr(d,"dns_probe",lambda h:d.Step("dns","PASS"))
 monkeypatch.setattr(d,"tcp_probe",lambda h,t:d.Step("tcp_443","PASS"))
 monkeypatch.setattr(d,"tls_probe",lambda h,t:d.Step("tls","PASS"))
 monkeypatch.setattr(d,"https_get",lambda h,p,t,k=None:d.Step("https_get_auth" if k else "https_get_public","PASS","GET_ONLY",200))
 secret="SECRET_123456789"
 r=d.diagnose("https://m99.eu",secret)
 assert secret not in repr(r) and not r["write_allowed"] and not r["write_performed"]
def test_exactly_three_http_probes_no_retry(monkeypatch):
 calls=[]
 monkeypatch.setattr(d,"dns_probe",lambda h:d.Step("dns","PASS"))
 monkeypatch.setattr(d,"tcp_probe",lambda h,t:d.Step("tcp_443","PASS"))
 monkeypatch.setattr(d,"tls_probe",lambda h,t:d.Step("tls","PASS"))
 def f(h,p,t,k=None):calls.append((p,bool(k)));return d.Step("https_get_auth" if k else "https_get_public","PASS","GET_ONLY",200)
 monkeypatch.setattr(d,"https_get",f);d.diagnose("https://m99.eu","K")
 assert calls==[("/",False),("/api",False),("/api",True)]
