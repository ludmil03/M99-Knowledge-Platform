from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
ADMIN_ROOT = REPO_ROOT / "admin-platform"
if str(ADMIN_ROOT) not in sys.path:
    sys.path.insert(0, str(ADMIN_ROOT))


import json
import pytest

from app.services.v073_phase46.live_product_truth_verifier import (
    ProductTruthError, _parse_product_nodes, verify_product_truth
)
from app.services.v073_phase46.secure_integration_settings import (
    SecureSettingsError, _normalize_back_office_template, save_m99eu_settings,
    public_m99eu_status, back_office_product_url
)

def product_xml(pid="2038", ref="M99-1", active="0", order="0", vis="none", cat="26", price="22.40", shop="1"):
    return f"""<prestashop><product><id>{pid}</id><reference>{ref}</reference><active>{active}</active><available_for_order>{order}</available_for_order><visibility>{vis}</visibility><id_category_default>{cat}</id_category_default><price>{price}</price><id_shop_default>{shop}</id_shop_default></product></prestashop>"""

def list_xml(*rows):
    return "<prestashop><products>"+"".join(r.replace("<prestashop>","").replace("</prestashop>","") for r in rows)+"</products></prestashop>"

def curl_ok(key,path,method="GET",body=None):
    return "200", product_xml()

def test_parse_single():
    r=_parse_product_nodes(product_xml());assert len(r)==1 and r[0]["id"]=="2038"

def test_invalid_xml():
    with pytest.raises(ProductTruthError):_parse_product_nodes("<bad")

def test_truth_three_sources_pass():
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",expected_category_id=26,expected_price="22.40",curl_fn=curl_ok)
    assert r.verified and len(r.evidence)>=5

def test_direct_404_blocks():
    def c(k,p,method="GET",body=None):
        return ("404","<prestashop/>") if p=="/api/products/2038" else ("200",product_xml())
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_id_filter_empty_blocks():
    def c(k,p,method="GET",body=None):
        return ("200","<prestashop><products/></prestashop>") if "filter%5Bid%5D" in p else ("200",product_xml())
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_ref_filter_empty_blocks():
    def c(k,p,method="GET",body=None):
        return ("200","<prestashop><products/></prestashop>") if "filter%5Breference%5D" in p else ("200",product_xml())
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_wrong_reference_blocks():
    def c(k,p,method="GET",body=None):return "200",product_xml(ref="OTHER")
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_wrong_active_blocks():
    def c(k,p,method="GET",body=None):return "200",product_xml(active="1")
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_wrong_orderable_blocks():
    def c(k,p,method="GET",body=None):return "200",product_xml(order="1")
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_wrong_visibility_blocks():
    def c(k,p,method="GET",body=None):return "200",product_xml(vis="both")
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_wrong_category_blocks():
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",expected_category_id=99,curl_fn=curl_ok);assert not r.verified

def test_wrong_price_blocks():
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",expected_price="99.00",curl_fn=curl_ok);assert not r.verified

def test_duplicate_list_blocks():
    dup=list_xml(product_xml(),product_xml())
    def c(k,p,method="GET",body=None):return "200", dup if "filter" in p else product_xml()
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c);assert not r.verified

def test_product_id_validation():
    with pytest.raises(ProductTruthError):verify_product_truth("A"*32,product_id=0,reference="M99-1",curl_fn=curl_ok)

def test_reference_validation():
    with pytest.raises(ProductTruthError):verify_product_truth("A"*32,product_id=1,reference="",curl_fn=curl_ok)

def test_bo_reject_list_url():
    with pytest.raises(SecureSettingsError):
        _normalize_back_office_template("https://m99.eu/private-admin/sell/catalog/products/?foo=1")

def test_bo_normalize_product_edit_url_and_strip_token():
    x=_normalize_back_office_template("https://m99.eu/private-admin/sell/catalog/products/2038/edit?_token=secret")
    assert x=="https://m99.eu/private-admin/sell/catalog/products/{id}/edit"

def test_bo_reject_host():
    with pytest.raises(SecureSettingsError):_normalize_back_office_template("https://evil.example/sell/catalog/products/")

def test_bo_roundtrip_encrypted(tmp_path):
    protect=lambda b:b[::-1]
    unprotect=lambda b:b[::-1]
    save_m99eu_settings(api_key="A"*32,enabled=True,back_office_url="https://m99.eu/private-admin/sell/catalog/products/2036/edit?_token=secret",repo_root=tmp_path,protect=protect)
    st=public_m99eu_status(repo_root=tmp_path);assert st["back_office_configured"]
    assert back_office_product_url(2038,repo_root=tmp_path,unprotect=unprotect)=="https://m99.eu/private-admin/sell/catalog/products/2038/edit"

def test_bo_blank_preserves(tmp_path):
    protect=lambda b:b[::-1]
    unprotect=lambda b:b[::-1]
    save_m99eu_settings(api_key="A"*32,enabled=True,back_office_url="https://m99.eu/private-admin/sell/catalog/products/2036/edit?_token=secret",repo_root=tmp_path,protect=protect)
    save_m99eu_settings(api_key="",enabled=True,back_office_url="",repo_root=tmp_path,protect=protect)
    assert back_office_product_url(99,repo_root=tmp_path,unprotect=unprotect).endswith("/99/edit")


def test_filter_id_path_is_curl_safe_percent_encoded():
    from app.services.v073_phase46.live_product_truth_verifier import _filter_path
    p=_filter_path("id","2038")
    assert p=="/api/products?filter%5Bid%5D=%5B2038%5D&display=full"
    assert "[" not in p and "]" not in p

def test_filter_reference_path_is_curl_safe_percent_encoded():
    from app.services.v073_phase46.live_product_truth_verifier import _filter_path
    p=_filter_path("reference","M99-1")
    assert "filter%5Breference%5D=%5BM99-1%5D" in p
    assert "[" not in p and "]" not in p

def test_transport_error_becomes_not_verified_not_crash():
    def c(k,p,method="GET",body=None):
        if "filter%5Bid%5D" in p:
            raise RuntimeError("curl exit code 3")
        return "200",product_xml()
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c)
    assert not r.verified
    assert any("ID-filter GET transport error" in x for x in r.blockers)

def test_all_three_transport_errors_become_blockers():
    def c(k,p,method="GET",body=None):
        raise RuntimeError("transport down")
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",curl_fn=c)
    assert not r.verified
    assert r.direct_http=="TRANSPORT_ERROR"
    assert r.id_filter_http=="TRANSPORT_ERROR"
    assert r.reference_filter_http=="TRANSPORT_ERROR"


def test_historical_empty_id_filter_mock_targets_encoded_runtime_url():
    from app.services.v073_phase46.live_product_truth_verifier import _filter_path
    p=_filter_path("id","2038")
    assert "filter%5Bid%5D" in p
    assert "filter[id]" not in p

def test_historical_empty_reference_filter_mock_targets_encoded_runtime_url():
    from app.services.v073_phase46.live_product_truth_verifier import _filter_path
    p=_filter_path("reference","M99-1")
    assert "filter%5Breference%5D" in p
    assert "filter[reference]" not in p


def structural_xml(pid="2038",ref="M99-1",shop="1",cat="26",langs=("1","2","3"),categories=("26",),stock=("500",)):
    lang_nodes="".join(f'<language id="{x}">Name{x}</language>' for x in langs)
    link_nodes="".join(f'<language id="{x}">slug-{x}</language>' for x in langs)
    cats="".join(f"<category><id>{x}</id></category>" for x in categories)
    stocks="".join(f"<stock_available><id>{x}</id></stock_available>" for x in stock)
    return f"""<prestashop><product><id>{pid}</id><reference>{ref}</reference><active>0</active><available_for_order>0</available_for_order><visibility>none</visibility><price>22.40</price><id_shop_default>{shop}</id_shop_default><id_category_default>{cat}</id_category_default><name>{lang_nodes}</name><link_rewrite>{link_nodes}</link_rewrite><associations><categories>{cats}</categories><images></images><combinations></combinations><stock_availables>{stocks}</stock_availables></associations></product></prestashop>"""

def test_structure_compare_same_shop_no_critical_warning():
    from app.services.v073_phase46.live_product_truth_verifier import _parse_product_structure, compare_product_structure
    a=_parse_product_structure(structural_xml());b=_parse_product_structure(structural_xml(pid="2036",ref="M99-OTHER"))
    summary,warnings=compare_product_structure(a,b)
    assert "TARGET_SHOP_DEFAULT=1" in summary and "SHOP_DEFAULT_MISMATCH" not in warnings

def test_structure_compare_shop_mismatch_warns():
    from app.services.v073_phase46.live_product_truth_verifier import _parse_product_structure, compare_product_structure
    a=_parse_product_structure(structural_xml(shop="1"));b=_parse_product_structure(structural_xml(pid="2036",ref="M99-OTHER",shop="2"))
    _,warnings=compare_product_structure(a,b);assert "SHOP_DEFAULT_MISMATCH" in warnings

def test_structure_compare_missing_category_warns():
    from app.services.v073_phase46.live_product_truth_verifier import _parse_product_structure, compare_product_structure
    a=_parse_product_structure(structural_xml(categories=()));b=_parse_product_structure(structural_xml(pid="2036",ref="M99-OTHER"))
    _,warnings=compare_product_structure(a,b);assert "TARGET_HAS_NO_CATEGORY_ASSOCIATIONS" in warnings

def test_structure_compare_missing_stock_warns():
    from app.services.v073_phase46.live_product_truth_verifier import _parse_product_structure, compare_product_structure
    a=_parse_product_structure(structural_xml(stock=()));b=_parse_product_structure(structural_xml(pid="2036",ref="M99-OTHER"))
    _,warnings=compare_product_structure(a,b);assert "TARGET_HAS_NO_STOCK_ASSOCIATION" in warnings

def test_structure_compare_language_mismatch_warns():
    from app.services.v073_phase46.live_product_truth_verifier import _parse_product_structure, compare_product_structure
    a=_parse_product_structure(structural_xml(langs=("1","2","3")));b=_parse_product_structure(structural_xml(pid="2036",ref="M99-OTHER",langs=("1","2")))
    _,warnings=compare_product_structure(a,b);assert "LANGUAGE_SET_DIFFERS_FROM_KNOWN_GOOD" in warnings

def test_compare_with_known_good_get_only():
    from app.services.v073_phase46.live_product_truth_verifier import compare_with_known_good
    calls=[]
    def c(k,p,method="GET",body=None):
        calls.append((p,method))
        if p.endswith("/2038"):return "200",structural_xml()
        if p.endswith("/2036"):return "200",structural_xml(pid="2036",ref="M99-OTHER")
        return "404","<prestashop/>"
    summary,warnings=compare_with_known_good("A"*32,target_product_id=2038,target_reference="M99-1",known_good_product_id=2036,curl_fn=c)
    assert summary and all(m=="GET" for _,m in calls) and len(calls)==2 and "SHOP_DEFAULT_MISMATCH" not in warnings

def test_bo_edit_url_rejects_wrong_route():
    with pytest.raises(SecureSettingsError):_normalize_back_office_template("https://m99.eu/private-admin/sell/catalog/products/2036")

def test_bo_edit_url_rejects_non_numeric_id():
    with pytest.raises(SecureSettingsError):_normalize_back_office_template("https://m99.eu/private-admin/sell/catalog/products/abc/edit")

def test_bo_edit_url_private_path_template():
    x=_normalize_back_office_template("https://m99.eu/adminABC123/sell/catalog/products/2036/edit?_token=redacted")
    assert x=="https://m99.eu/adminABC123/sell/catalog/products/{id}/edit" and "_token" not in x

def test_truth_with_known_good_keeps_api_verified_separate_from_structural_warnings():
    def c(k,p,method="GET",body=None):
        if p=="/api/products/2036":return "200",structural_xml(pid="2036",ref="M99-OTHER",shop="2")
        if p=="/api/products/2038":return "200",structural_xml()
        return "200",product_xml()
    r=verify_product_truth("A"*32,product_id=2038,reference="M99-1",known_good_product_id=2036,curl_fn=c)
    assert r.verified is True and "SHOP_DEFAULT_MISMATCH" in r.structural_warnings
