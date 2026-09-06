from app.services.v073_phase45.r37_import_bridge import _host

def test_host_normalization():
    assert _host("https://www.calenda.bg/path") == "calenda.bg"
    assert _host("calenda.bg") == "calenda.bg"
    assert _host("") == ""
