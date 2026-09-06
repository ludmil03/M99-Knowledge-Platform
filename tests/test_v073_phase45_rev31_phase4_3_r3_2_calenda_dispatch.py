from app.services.v073_phase45.unified_add_products import (
    SourceView, connector_status, normalize_domain
)

def test_calenda_dispatch_is_ready():
    s = SourceView("x","SUPPLIER","Календа","calenda.bg","https://calenda.bg","ACTIVE")
    st = connector_status(s)
    assert normalize_domain(s.domain) == "calenda.bg"
    assert st.kind == "CALENDA_PUBLIC"
    assert st.state == "READY"

def test_palltex_and_stenso_dispatch_preserved():
    p = SourceView("p","SUPPLIER","Palltex","palltex.bg","https://palltex.bg","ACTIVE")
    s = SourceView("s","SUPPLIER","Stenso","stenso.net","https://stenso.net","ACTIVE")
    assert connector_status(p).kind == "PALLTEX_PUBLIC"
    assert connector_status(s).kind == "STENSO_REFERENCE"
