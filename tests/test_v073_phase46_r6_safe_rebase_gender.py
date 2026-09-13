import sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; ADMIN=ROOT/"admin-platform"
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
import app.services.v073_phase46.content_manufacturer_intelligence as svc

def test_female_shirt_title_is_not_male():
    p={"name":"ДАМСКА РИЗА TEST","brand":"BRAND","product_type":"shirt","gender":"female","oxford":True}
    assert svc._localized_title(p,"BG").startswith("Дамска риза")
    assert "Мъжка" not in svc._localized_title(p,"BG")
    assert "Women's" in svc._localized_title(p,"EN")

def test_male_river_compatibility_remains():
    p={"name":"RIVER","brand":"PROMO STARS","product_type":"shirt","gender":"male","oxford":True}
    assert "Мъжка риза" in svc._localized_title(p,"BG")
    assert "RIVER" in svc._localized_title(p,"EN")

def test_unisex_shirt_has_neutral_title():
    p={"name":"GENERIC","brand":"BRAND","product_type":"shirt","gender":"unisex","oxford":False}
    assert svc._localized_title(p,"BG").startswith("Риза ")
