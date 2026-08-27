from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TEMPLATE=ROOT/'admin-platform/app/templates/supplier_browser/index.html'
SERVICE=ROOT/'admin-platform/app/services/supplier_browser.py'
ROUTER=ROOT/'admin-platform/app/routers/supplier_browser.py'

def test_gui_runtime_contract():
    t=TEMPLATE.read_text(encoding='utf-8')
    assert '(title pending product read)' not in t
    assert 'Избрани: 0' in t
    assert 'STENSO REF:' in t
    assert 'PRICE:' in t
    assert 'Размери:' in t
    assert 'Спецификации' in t
    assert 'Официален сайт на производителя' in t
    line=next(x for x in t.splitlines() if 'class="product-check"' in x)
    assert 'checked' not in line
    # Revision 20+ progressive contract:
    # product checkboxes start disabled in HTML and are enabled by JS only
    # after the individual live hydration returns PASS.
    assert 'class="product-check"' in t
    assert 'value="{{p.url}}" disabled' in t
    assert "const ok=p.hydration_status==='PASS';" in t
    assert "cb.disabled=!ok;" in t
    assert "runHydrationQueue(4)" in t

def test_service_has_live_hydration():
    t=SERVICE.read_text(encoding='utf-8')
    for marker in ('hydrate_stenso_product','hydrate_stenso_products','supplier_reference','price_text','variants'):
        assert marker in t

def test_create_job_reverifies_supplier_url():
    t=ROUTER.read_text(encoding='utf-8')
    assert 'hydrate_stenso_product(selected_url' in t
