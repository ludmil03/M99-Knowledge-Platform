from pathlib import Path
P=Path(__file__).resolve().parents[1]/"admin-platform/app/routers/r7k4_real_operator_publish.py"
def s(): return P.read_text(encoding="utf-8")
def test_visible_preview_optional():
    x=s()
    assert '<input name=price_override value="{_e(price_override)}" placeholder="незадължително за проверката">' in x
    assert '<input name=price_override required value=' not in x
def test_publish_safety_contract():
    x=s()
    assert "publish_palltex_controlled" in x
    assert "operator_approved" in x
    p=x.index('@router.post("/publish"')
    assert "price_override" in x[p:]
def test_selector_preserved():
    assert "<select name=item_id required>" in s()
def test_no_new_network_write_client():
    x=s().lower()
    assert all(v not in x for v in ("requests.post","requests.put","httpx.post","urllib.request"))
