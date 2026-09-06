from app.services.v073_phase45.calenda_public_connector import _parse,_variants_from_live_controls

HTML="""<div class="choose-color">
<div data-color-id="20" data-image="/media/31809/white.jpg"><span>20</span><span>бял</span></div>
<button data-color="26" data-img="/media/31809/black.jpg">26 черно</button>
<a href="/products/31809?color=42" data-image="/media/31809/navy.jpg">42 тъмно-синьо</a>
<span onclick="selectColor('46')" data-color-code="46" data-photo="/media/31809/sky.jpg">46 небесно-синьо</span>
</div><h3>Свързани продукти:</h3><a href="/products/93300?color=10">10 unrelated</a>"""

def variants(): return _variants_from_live_controls(_parse(HTML),"https://calenda.bg/products/31809")
def test_exact_colors(): assert [v["code"] for v in variants()]==["20","26","42","46"]
def test_own_images(): assert len({v["image_url"] for v in variants()})==4 and all(v["image_url"] for v in variants())
def test_related_excluded(): assert "10" not in {v["code"] for v in variants()}
