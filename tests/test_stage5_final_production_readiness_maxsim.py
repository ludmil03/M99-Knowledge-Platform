from decimal import Decimal
import xml.etree.ElementTree as ET
from app.services.stage5_production_readiness import gross_to_net,build_blank_create_xml
def test_gross_to_net_decimal():
 assert gross_to_net("58.13","0.20")==Decimal("48.441667")
def test_blank_schema_binding_dynamic_languages():
 x="""<prestashop><product><id_category_default/><price/><id_tax_rules_group/><reference/><active/><available_for_order/><visibility/><name/><description_short/><description/><meta_title/><meta_description/></product></prestashop>"""
 c={k:{"name":"N "+k,"short":"S "+k,"long":"L "+k,"meta_title":"T "+k,"meta_description":"D "+k} for k in ("en","bg","ru")}
 out=build_blank_create_xml(x,reference="M99 100019",category_id=7,net_price="48.441667",tax_rules_group_id=3,language_map={"en":1,"bg":2,"ru":3},content=c)
 r=ET.fromstring(out)
 assert r.findtext(".//reference")=="M99 100019"
 assert r.findtext(".//price")=="48.441667"
 assert r.findtext(".//id_tax_rules_group")=="3"
 assert r.findtext(".//active")=="0"
 assert len(r.findall(".//name/language"))==3
