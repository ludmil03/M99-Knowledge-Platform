from app.services.v073_phase46.product_2041_live_readonly_preflight import inspect
def X(tax="0",comb="",img="",cache=""):
 return f"<prestashop><product><id>2041</id><reference>M99 100018</reference><active>0</active><available_for_order>0</available_for_order><visibility>none</visibility><id_category_default>26</id_category_default><price>25</price><id_tax_rules_group>{tax}</id_tax_rules_group><cache_default_attribute>{cache}</cache_default_attribute><associations><combinations>{comb}</combinations><images>{img}</images></associations></product></prestashop>"
def test_blocks():assert set(inspect("x",lambda a,b:("200",X()))["blockers"])>={"VAT_RULE_UNRESOLVED","NO_IMAGES","NO_COMBINATIONS"}
def test_good():
 c="<combination><id>9</id></combination>";i="<image><id>8</id></image>";assert not inspect("x",lambda a,b:("200",X("5",c,i,"9")))["blockers"]
def test_readonly():assert inspect("x",lambda a,b:("200",X()))["writes_performed"] is False
