from pathlib import Path
import json, sys
from dataclasses import dataclass
from collections import namedtuple
import pytest

ADMIN=Path(__file__).resolve().parents[1]/"admin-platform"
if str(ADMIN) not in sys.path: sys.path.insert(0,str(ADMIN))
from app.services.v073_phase45 import palltex_product_hydration_adapter as a
URL="https://palltex.bg/bg/p/generic-product-antracit/17374"

def mkhtml(*,sku="042554",sizes=("XS","S","M","L","XL","2XL","3XL","4XL"),color="Антрацит",
           label="Код на артикул",selector=True,extra="",jsonld=None):
    sku_line=f"<div>{label}: {sku}</div>" if sku is not None else ""
    opts="".join(f"<button>{s}</button>" for s in sizes)
    selector_html=f"<section><h3>Избери размер</h3>{opts}<div>Моля изберете размер</div></section>" if selector else ""
    jl=f'<script type="application/ld+json">{json.dumps(jsonld,ensure_ascii=False)}</script>' if jsonld is not None else ""
    return f"<html><body>{jl}<h1>GENERIC</h1>{sku_line}<div>Цвят: {color}</div>{selector_html}{extra}</body></html>"

@dataclass(frozen=True)
class R:
    source_key:str="PALLTEX_PUBLIC"; name:str="GENERIC"; url:str=URL
    supplier_reference:str|None=None; brand:str|None="GENERIC"; price_text:str|None="30.99"
    currency:str|None="EUR"; availability_text:str|None="INSTOCK"; description:str|None="x"
    images:tuple[str,...]=("https://palltex.bg/media/x.jpg",); variants:tuple[dict,...]=()
    hydration_pass:bool=False
    warnings:tuple[str,...]=("SUPPLIER_REFERENCE_NOT_FOUND","PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER")

# 16
@pytest.mark.parametrize("label",["Код на артикул","Артикулен код","SKU","Код продукт"])
@pytest.mark.parametrize("ref",["042554","A-100","AB_12","X.9/2"])
def test_same_node_supplier_reference_labels_and_formats(label,ref):
    assert a.parse_palltex_product_html(mkhtml(sku=ref,label=label),URL)["supplier_reference"]==ref

# 8
@pytest.mark.parametrize("token",["XS","S","M","XL","2XL","42","48","17374"])
def test_empty_label_never_steals_following_token(token):
    h=f"<html><body><div>Код на артикул:</div><div>{token}</div><div>Цвят: Антрацит</div><h3>Избери размер</h3><button>S</button></body></html>"
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]==""

# 6
@pytest.mark.parametrize("ref",["x","код","☃☃","A B C","A"*70,"<bad>"])
def test_malformed_reference_rejected(ref):
    assert a.parse_palltex_product_html(mkhtml(sku=ref),URL)["supplier_reference"]==""

# 3
@pytest.mark.parametrize("payload,expected",[
    ({"@type":"Product","sku":"00991"},"00991"),
    ({"@graph":[{"@type":"BreadcrumbList"},{"@type":"Product","sku":"ZX-8"}]},"ZX-8"),
    ({"@type":"Product","mpn":"MPN-77"},"MPN-77"),
])
def test_jsonld_product_reference(payload,expected):
    assert a.parse_palltex_product_html(mkhtml(sku=None,jsonld=payload),URL)["supplier_reference"]==expected

# 8
@pytest.mark.parametrize("sizes",[
 ("XS","S","M","L","XL"),("2XS","XS","S","M","L","XL","2XL","3XL","4XL"),
 ("36","38","40","42","44","46","48"),("39","40","41","42","43","44","45","46","47","48"),
 ("S","M"),("XL","2XL"),("32","34","36"),("48","50","52","54","56"),
])
def test_size_order_preserved(sizes):
    p=a.parse_palltex_product_html(mkhtml(sizes=sizes),URL)
    assert p["sizes"]==list(sizes) and len(p["variants"])==1

# 25 single cases = total 66
def test_unrelated_numbers_outside_selector_ignored():
    assert a.parse_palltex_product_html(mkhtml(sizes=("S","M","L"),extra="<div>2026 99999 17374 240</div>"),URL)["sizes"]==["S","M","L"]

def test_no_selector_no_invented_sizes():
    p=a.parse_palltex_product_html(mkhtml(selector=False),URL); assert p["sizes"]==[] and not p["saw_size_selector"] and len(p["variants"])==1

def test_selector_without_valid_sizes_no_variants():
    p=a.parse_palltex_product_html(mkhtml(sizes=("Цена","Наличност","99999")),URL); assert p["saw_size_selector"] and p["sizes"]==[] and p["variants"]==[]

def test_color_preserved():
    assert a.parse_palltex_product_html(mkhtml(color="Тъмно син"),URL)["color"]=="Тъмно син"

def test_url_id_not_supplier_reference():
    p=a.parse_palltex_product_html(mkhtml(sku=None),URL); assert p["supplier_reference"]=="" and p["supplier_reference"]!="17374"

@pytest.mark.parametrize("url",[
 "http://palltex.bg/bg/p/x/17374","https://example.com/bg/p/x/17374","https://palltex.bg/category/17374",
 "https://palltex.bg/bg/p/x/not-a-number","file:///etc/passwd",
])
def test_invalid_urls_rejected(url):
    with pytest.raises(a.PalltexHydrationAdapterError): a._validate_public_host(url,resolve=False)

def test_valid_url_accepted_without_dns():
    assert a._validate_public_host(URL,resolve=False)==URL

def test_missing_sku_keeps_blocker(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(sku=None),URL,image_url=image_url))
    r=a.enhance_hydrated_result(R(),URL); assert "SUPPLIER_REFERENCE_NOT_FOUND" in r.warnings and not r.hydration_pass

def test_missing_valid_sizes_keeps_variant_blocker(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(sku="A-100",sizes=("Цена","99999")),URL,image_url=image_url))
    r=a.enhance_hydrated_result(R(),URL); assert "PALLTEX_VARIANTS_REQUIRE_VALIDATED_PRODUCT_VARIANT_PARSER" in r.warnings and not r.hydration_pass

def test_both_known_blockers_solved(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    r=a.enhance_hydrated_result(R(),URL); assert r.supplier_reference=="042554" and r.warnings==() and r.hydration_pass

def test_unknown_warning_survives(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    r=a.enhance_hydrated_result(R(warnings=R().warnings+("OTHER_HARD_BLOCKER",)),URL); assert "OTHER_HARD_BLOCKER" in r.warnings and not r.hydration_pass

def test_read_failure_blocks(monkeypatch):
    def boom(*args,**kwargs): raise a.PalltexHydrationAdapterError("boom")
    monkeypatch.setattr(a,"fetch_and_parse",boom)
    r=a.enhance_hydrated_result(R(),URL); assert "PALLTEX_ADAPTER_READ_FAILED" in r.warnings and not r.hydration_pass

def test_no_m99_stock_or_quantity_invented():
    p=a.parse_palltex_product_html(mkhtml(),URL); v=p["variants"][0]
    assert "M99_PHYSICAL_STOCK" in v["availability_semantics"]
    for row in v["sizes"]:
        assert row["availability"]=="SUPPLIER_VISIBLE" and "quantity" not in row and "M99_STOCK" in row["availability_semantics"]

def test_dict_result_supported(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    r=a.enhance_hydrated_result({"warnings":list(R().warnings),"hydration_pass":False,"images":[]},URL)
    assert r["supplier_reference"]=="042554" and r["hydration_pass"]

def test_namedtuple_result_supported(monkeypatch):
    NT=namedtuple("NT","supplier_reference variants warnings hydration_pass images"); start=NT(None,(),R().warnings,False,())
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    r=a.enhance_hydrated_result(start,URL); assert r.supplier_reference=="042554" and r.hydration_pass

def test_non_palltex_result_unchanged():
    r=R(); assert a.enhance_hydrated_result(r,"https://example.com/p/1") is r

def test_install_adapter_wraps(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    class C:
        __module__="fake_mod"
        def get_product(self,url): return R()
    ns={"__name__":"fake_mod","Connector":C}; assert a.install_adapter(ns)==("Connector.get_product",)
    assert C().get_product(URL).hydration_pass

def test_install_adapter_idempotent(monkeypatch):
    monkeypatch.setattr(a,"fetch_and_parse",lambda url,image_url="":a.parse_palltex_product_html(mkhtml(),URL,image_url=image_url))
    class C:
        __module__="fake_mod2"
        def get_product(self,url): return R()
    ns={"__name__":"fake_mod2","Connector":C}; x=a.install_adapter(ns); y=a.install_adapter(ns); assert x==y==("Connector.get_product",)

def test_install_without_target_stops():
    class C: __module__="fake_none"
    with pytest.raises(a.PalltexHydrationAdapterError): a.install_adapter({"__name__":"fake_none","Connector":C})

def test_exact_regression_empty_label_followed_by_xs():
    h="<html><body><div>Код на артикул:</div><div>XS</div><div>Цвят: Антрацит</div></body></html>"
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]==""

def test_live_shape_contract():
    h="""<html><body><h1>Generic trousers</h1><div>Марка: GENERIC</div><div>Наличност: В наличност</div>
    <div>Код на артикул: 042554</div><div>Цвят: Антрацит</div><div>* Избери размер Размер:</div>
    <button>XS</button><button>S</button><button>M</button><button>L</button><button>XL</button>
    <button>2XL</button><button>3XL</button><button>4XL</button><div>Моля изберете размер</div></body></html>"""
    p=a.parse_palltex_product_html(h,URL); assert p["supplier_reference"]=="042554" and p["sizes"]==["XS","S","M","L","XL","2XL","3XL","4XL"]

# R7J R4 live-DOM context regression suite (22 cases)

@pytest.mark.parametrize("ref",["042554","000123","AB-123","X_77"])
def test_r4_split_node_reference_in_product_context(ref):
    h=f"""<html><body><div>Марка: GENERIC</div><div>Наличност: В наличност</div>
    <div>Код на артикул:</div><div>{ref}</div><div>Цвят:</div><div>Антрацит</div>
    <h3>Избери размер</h3><button>XS</button><button>S</button></body></html>"""
    p=a.parse_palltex_product_html(h,URL)
    assert p["supplier_reference"]==ref
    assert p["color"]=="Антрацит"

@pytest.mark.parametrize("token",["XS","S","M","L","XL","2XL","3XL","4XL","36","38","40","42"])
def test_r4_split_size_token_never_reference(token):
    h=f"""<html><body><div>Марка: G</div><div>Код на артикул:</div><div>{token}</div>
    <div>Цвят:</div><div>Антрацит</div><div>Избери размер</div></body></html>"""
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]==""

@pytest.mark.parametrize("ref",["042554","A-100","00991"])
def test_r4_split_reference_without_context_rejected(ref):
    h=f"<html><body><div>Код на артикул:</div><div>{ref}</div><footer>Контакти</footer></body></html>"
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]==""

def test_r4_url_product_id_never_promoted_even_with_context():
    h="""<html><body><div>Марка: G</div><div>Код на артикул:</div><div>17374</div>
    <div>Цвят:</div><div>Антрацит</div><div>Избери размер</div><button>S</button></body></html>"""
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]==""

def test_r4_selected_color_beats_swatch_list():
    h="""<html><body><div>Цвят:</div><a>Бял</a><a>Тъмно син</a><a>Черен</a><a>Антрацит</a>
    <h1>GENERIC</h1><div>Марка: G</div><div>Наличност: В наличност</div>
    <div>Код на артикул:</div><div>042554</div><div>Цвят:</div><div>Антрацит</div>
    <div>Избери размер</div><button>XS</button><button>S</button><button>M</button>
    <button>L</button><button>XL</button><button>2XL</button><button>3XL</button><button>4XL</button></body></html>"""
    p=a.parse_palltex_product_html(h,URL)
    assert p["supplier_reference"]=="042554"
    assert p["color"]=="Антрацит"
    assert p["sizes"]==["XS","S","M","L","XL","2XL","3XL","4XL"]
    assert len(p["variants"])==1

def test_r4_split_leading_zero_preserved():
    h="""<html><body><div>Марка: G</div><div>Код на артикул:</div><div>000042554</div>
    <div>Цвят:</div><div>Антрацит</div><div>Избери размер</div><button>S</button></body></html>"""
    assert a.parse_palltex_product_html(h,URL)["supplier_reference"]=="000042554"
