import unittest
from core.live_channel_metadata import parse_languages_xml, parse_categories_xml
from core.s3s_content_quality_v06642 import build_content_preview

LANGS="""<prestashop><languages><language><id>1</id><iso_code>en</iso_code><name>English</name><active>1</active></language><language><id>2</id><iso_code>bg</iso_code><name>Bulgarian</name><active>1</active></language></languages></prestashop>"""
CATS="""<prestashop><categories><category><id>93</id><active>1</active><name><language id='1'>Test</language><language id='2'>Test</language></name></category></categories></prestashop>"""
FACTS={'model_name':'GLOVE A.BOX LOW PRO S3S','manufacturer_item':'701.183119_80013','protection_class':'S3S','colour':'BLACK','toe_cap':'aluminium 200J','anti_puncture':'K SOLE Ultralite','width':'11','technology':['A.Box System','Ariatex membrane'],'esd':True,'midsole':'EVA','outsole':'FO HRO SR nitrile rubber','eu_sizes':[str(x) for x in range(35,49)]}
class T(unittest.TestCase):
 def test_live_language_mapping_does_not_assume_ids(self):
  r=parse_languages_xml(LANGS); self.assertEqual(r['en_id'],'1'); self.assertEqual(r['bg_id'],'2'); self.assertTrue(r['ready'])
 def test_test_category_93_is_discovered(self):
  r=parse_categories_xml(CATS,'Test'); self.assertEqual(r['selected_category_id'],'93'); self.assertTrue(r['ready'])
 def test_content_has_faq_both_languages(self):
  p=build_content_preview(FACTS); self.assertIn('Често задавани въпроси',p['bg']['long_description_html']); self.assertIn('Frequently asked questions',p['en']['long_description_html'])
 def test_content_has_evidence_trace(self):
  p=build_content_preview(FACTS); self.assertEqual(p['evidence_trace']['manufacturer_item'],'701.183119_80013')
