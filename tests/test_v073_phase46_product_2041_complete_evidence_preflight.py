from app.services.v073_phase46.product_2041_complete_evidence_preflight import inspect
P="<prestashop><product><id>2041</id><reference>M99 100018</reference><active>0</active><available_for_order>0</available_for_order><visibility>none</visibility><id_category_default>26</id_category_default><price>30.2</price><id_tax_rules_group>0</id_tax_rules_group><cache_default_attribute>0</cache_default_attribute><associations><combinations/><images/></associations></product></prestashop>"
T="<prestashop><tax_rule_groups><tax_rule_group><id>5</id><name>Standard</name><active>1</active></tax_rule_group></tax_rule_groups></prestashop>"
def c(k,p): return ("200",P if "/products/" in p else T)
def test_readonly(): assert inspect("x",c)["writes_performed"] is False
def test_identity(): assert inspect("x",c)["current"]["reference"]=="M99 100018"
def test_tax_discovery(): assert inspect("x",c)["evidence"]["tax_candidates"][0]["id"]=="5"
def test_supplier_failclosed(): assert "SUPPLIER_PRICE_NOT_VERIFIED" in inspect("x",c)["blockers"]
def test_image_failclosed(): assert "IMAGE_EVIDENCE_MISSING" in inspect("x",c)["blockers"]
def test_variant_failclosed(): assert "VARIANT_EVIDENCE_MISSING" in inspect("x",c)["blockers"]
