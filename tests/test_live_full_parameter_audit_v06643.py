import unittest
from core.live_full_parameter_audit_v06643 import parse_product_xml,content_seo_metrics,diff_dicts,analyze_html,quality_observations
A='<prestashop><product><id>2076</id><reference>MELA-REF</reference><name><language id="1">EN</language><language id="2">BG</language></name><description><language id="1"><![CDATA[<h2>Features</h2><h3>FAQ</h3>]]></language><language id="2"><![CDATA[<h2>Характеристики</h2><h3>Често задавани въпроси</h3>]]></language></description><associations><images><image><id>5</id></image></images><combinations><combination><id>10</id></combination></combinations></associations></product></prestashop>'
B=A.replace("<id>2076</id>","<id>2100</id>",1).replace("MELA-REF","",1).replace("<combination><id>10</id></combination>","")
class T(unittest.TestCase):
    def test_parse(self):
        s=parse_product_xml(A); self.assertEqual(s["scalar_fields"]["id"],"2076"); self.assertEqual(len(s["associations"]["images"]),1)
    def test_lang(self):
        m=content_seo_metrics(parse_product_xml(A),{"bg":"2","en":"1"}); self.assertEqual(m["bg"]["name"],"BG"); self.assertTrue(m["bg"]["has_h2"]); self.assertTrue(m["bg"]["faq_present"])
    def test_html(self):
        x=analyze_html("<h1>A</h1><h2>B</h2><h3>C</h3> FAQ"); self.assertEqual(x["heading_counts"]["h3"],1); self.assertTrue(x["faq_present"])
    def test_diff(self):
        d=diff_dicts(parse_product_xml(A)["scalar_fields"],parse_product_xml(B)["scalar_fields"]); self.assertTrue(any(x["path"]=="id" for x in d))
    def test_no_winner(self):
        a=content_seo_metrics(parse_product_xml(A),{"bg":"2","en":"1"}); q=quality_observations(a,a); self.assertIsNone(q["global_winner"])
