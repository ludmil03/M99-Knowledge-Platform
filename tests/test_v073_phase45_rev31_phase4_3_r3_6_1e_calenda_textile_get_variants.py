from app.services.v073_phase45 import calenda_public_connector as c

HTML = """
<div id="product-image">
  <div id="product_carousel"><img src="https://calenda.bg/storage/products/93100dd7d.jpg"/></div>
  <div><h3>Изберете цвят</h3></div>
  <div id="textileProductColors">
    <div class="textile-color "><form method="GET"><input type="hidden" name="color" value="7"/><button>20</button><div>БЯЛ</div></form></div>
    <div class="textile-color "><form method="GET"><input type="hidden" name="color" value="206"/><button>26</button><div>черно</div></form></div>
    <div class="textile-color "><form method="GET"><input type="hidden" name="color" value="211"/><button>42</button><div>тъмно-синьо</div></form></div>
    <div class="textile-color "><form method="GET"><input type="hidden" name="color" value="231"/><button>46</button><div>небесно-синьо</div></form></div>
  </div>
</div>
<div id="product-right"></div>
"""

def test_exact_live_form_mapping():
    variants = c._variants_from_textile_forms(HTML, "https://calenda.bg/products/31809")
    assert [(v["code"], v["value"], v["source_variant_id"]) for v in variants] == [
        ("20", "БЯЛ", "7"),
        ("26", "черно", "206"),
        ("42", "тъмно-синьо", "211"),
        ("46", "небесно-синьо", "231"),
    ]

def test_get_urls_use_source_ids():
    variants = c._variants_from_textile_forms(HTML, "https://calenda.bg/products/31809")
    assert [v["url"] for v in variants] == [
        "https://calenda.bg/products/31809?color=7",
        "https://calenda.bg/products/31809?color=206",
        "https://calenda.bg/products/31809?color=211",
        "https://calenda.bg/products/31809?color=231",
    ]

def test_requested_source_id_maps_to_visible_code():
    variants = c._variants_from_textile_forms(HTML, "https://calenda.bg/products/31809?color=206")
    hit = [v for v in variants if c._requested_variant_matches(v, "206")]
    assert len(hit) == 1
    assert hit[0]["code"] == "26"

def test_per_variant_image_hydration(monkeypatch):
    variants = c._variants_from_textile_forms(HTML, "https://calenda.bg/products/31809")
    image_by_query = {
        "color=7": "https://calenda.bg/storage/products/93100_20.jpg",
        "color=206": "https://calenda.bg/storage/products/93100_26.jpg",
        "color=211": "https://calenda.bg/storage/products/93100_42.jpg",
        "color=231": "https://calenda.bg/storage/products/93100_46.jpg",
    }

    def fake_fetch(url):
        image = next(v for k, v in image_by_query.items() if k in url)
        page = f'<meta property="og:image" content="{image}"><div id="product-image"><img src="{image}" alt="MЪЖКА РИЗА RIVER"></div>'
        return 200, url, page

    monkeypatch.setattr(c, "_fetch", fake_fetch)
    hydrated = c._hydrate_variant_images(variants, "MЪЖКА РИЗА RIVER", "93100")
    assert len(hydrated) == 4
    assert all(v["image_url"] for v in hydrated)
    assert len({v["image_url"] for v in hydrated}) == 4
