from app.services.v073_phase45 import calenda_public_connector as c

def page(ref, code, related="99999_88a.jpg"):
    return f"""
    <div id="product-image">
      <div id="product_carousel">
        <img src="https://calenda.bg/storage/products/{ref}dd7d.jpg">
      </div>
    </div>
    <table id="textile-color-table">
      <tr><td><img src="https://calenda.bg/storage/products/{ref}_{code}a.jpg"></td></tr>
    </table>
    <script>
    $(document).ready(function(){{
      $('#product_carousel').trigger('add.owl.carousel',
      ['<div><a href="https://calenda.bg/storage/products/{ref}_{code}a.jpg"><img src="https://calenda.bg/storage/products/{ref}_{code}a.jpg"/></a></div>']);
    }});
    </script>
    <div id="moreProducts">
      <img src="https://calenda.bg/storage/products/{related}">
    </div>
    """

def test_variant_image_prefers_selected_color_carousel_evidence():
    html = page("93100", "20")
    got = c._variant_image_from_html(html, "https://calenda.bg/products/31809?color=7", "93100", "20")
    assert got == "https://calenda.bg/storage/products/93100_20a.jpg"

def test_four_colors_map_to_four_distinct_images():
    codes = ["20", "26", "42", "46"]
    got = [
        c._variant_image_from_html(page("93100", code), "https://calenda.bg/products/31809", "93100", code)
        for code in codes
    ]
    assert got == [f"https://calenda.bg/storage/products/93100_{code}a.jpg" for code in codes]
    assert len(set(got)) == 4

def test_wrong_color_and_related_product_are_rejected():
    html = page("93100", "20")
    assert c._variant_image_from_html(html, "https://calenda.bg/products/31809", "93100", "26") is None
