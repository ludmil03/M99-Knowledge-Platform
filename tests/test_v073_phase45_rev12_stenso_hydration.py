from pathlib import Path
import importlib.util

ROOT = Path(__file__).resolve().parents[1]
SERVICE = ROOT / "admin-platform" / "app" / "services" / "supplier_browser.py"
TEMPLATE = ROOT / "admin-platform" / "app" / "templates" / "supplier_browser" / "index.html"
ROUTER = ROOT / "admin-platform" / "app" / "routers" / "supplier_browser.py"

def load_service():
    spec = importlib.util.spec_from_file_location("m99_supplier_browser_phase45_rev11", SERVICE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

PRODUCT_HTML = """
<html><body>
<h1>Боти MARINE O2 FO SRC 06200280</h1>
<div class="product-prices"><span class="price">124,90 лв.</span></div>
<div>Арт. №: 06200280</div>
<div class="product-cover"><img src="/img/marine-main.webp" alt="Боти MARINE О2 FO SRC"></div>
<div class="product-images"><img data-src="/img/marine-2.webp"></div>
<div id="description">
  Надеждни водоотблъскващи обувки.
  САЯ: естествена кожа
  ПОДПЛАТА: дишаща материя
</div>
<div class="sizes">
  <button class="size disabled">36</button>
  <button class="size unavailable">37</button>
  <button class="size">38</button>
  <button class="size active">39</button>
</div>
</body></html>
"""

CATEGORY_HTML = """
<html><head><title>Работно облекло</title></head><body>
<article class="product-miniature"><a href="/produkt/boti/4344-marine">Marine</a></article>
</body></html>
"""

def test_stenso_hydration_extracts_required_contract(monkeypatch):
    m = load_service()
    monkeypatch.setattr(m, "fetch_html", lambda url, timeout=20.0: ("https://stenso.net/produkt/boti/4344-marine", PRODUCT_HTML, 200))
    p = m.hydrate_stenso_product("https://stenso.net/produkt/boti/4344-marine")
    assert p["title"] == "Боти MARINE O2 FO SRC"
    assert p["supplier_reference"] == "06200280"
    assert "124,90" in p["price_text"]
    assert len(p["images"]) == 2
    assert "Надеждни" in p["description"]
    specs = {x["name"]: x["value"] for x in p["specifications"]}
    assert specs["САЯ"] == "естествена кожа"
    assert specs["ПОДПЛАТА"] == "дишаща материя"
    by = {v["value"]: v["availability"] for v in p["variants"]}
    assert by["36"] == "OUT_OF_STOCK"
    assert by["37"] == "OUT_OF_STOCK"
    assert by["38"] == "IN_STOCK"
    assert by["39"] == "IN_STOCK"
    assert p["availability_text"] == "PARTIAL_VARIANT_AVAILABILITY"

def test_category_discovers_waiting_product_then_separate_hydration_passes(monkeypatch):
    m = load_service()
    calls = []

    def fake_fetch(url, timeout=25.0):
        calls.append(url)
        if "/produkt/" in url:
            return ("https://stenso.net/produkt/boti/4344-marine", PRODUCT_HTML, 200)
        return ("https://stenso.net/211-test", CATEGORY_HTML, 200)

    monkeypatch.setattr(m, "fetch_html", fake_fetch)

    # Progressive contract: category inspection must be fast and must NOT
    # hydrate every product synchronously.
    result = m.inspect_supplier_page("https://stenso.net/211-test", "https://stenso.net")
    assert result["type"] == "category"
    assert result["hydration_pass"] == 0
    assert result["hydration_fail"] == 0
    assert len(result["products"]) == 1
    assert result["products"][0]["hydration_status"] == "WAITING"
    assert result["products"][0]["supplier_reference"] == ""
    assert len(calls) == 1
    assert "/produkt/" not in calls[0]

    # Product hydration is a separate operation and must still prove the
    # original product-data contract.
    product = m.hydrate_stenso_product(
        result["products"][0]["url"],
        "https://stenso.net",
        use_cache=False,
    )
    assert product["hydration_status"] == "PASS"
    assert product["supplier_reference"] == "06200280"
    assert product["title"] == "Боти MARINE O2 FO SRC"
    assert len(calls) == 2
    assert "/produkt/" in calls[1]

def test_gui_defaults_to_zero_selected_products():
    text = TEMPLATE.read_text(encoding="utf-8")
    checkbox_line = next(x for x in text.splitlines() if 'class="product-check"' in x)
    assert " checked" not in checkbox_line
    assert "Избрани: 0" in text
    assert 'id="create-draft-btn"' in text and "disabled" in text

def test_create_job_reverifies_selected_supplier_urls():
    text = ROUTER.read_text(encoding="utf-8")
    assert "hydrate_stenso_product(selected_url" in text
    assert 'form.getlist("selected_title")' not in text
    assert 'form.getlist("selected_ref")' not in text
