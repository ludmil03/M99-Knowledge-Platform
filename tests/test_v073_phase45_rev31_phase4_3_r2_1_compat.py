from app.services.v073_phase45.unified_add_products import SourceView, validate_selection, _classify

def test_r1_selection_api_preserved():
    s = SourceView("s1","SUPPLIER","Palltex","palltex.bg","https://palltex.bg/","ACTIVE")
    mode, urls = validate_selection("ONE_PRODUCT", ["https://palltex.bg/product/1"], s)
    assert mode == "ONE_PRODUCT"
    assert urls == ("https://palltex.bg/product/1",)

def test_r1_classifier_api_preserved():
    assert _classify("https://x.bg/category/work-shoes", "Работни обувки")[0] == "category"
    assert _classify("https://x.bg/product/123", "Product 123")[0] == "product"
