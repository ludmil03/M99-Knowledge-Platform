import unittest
from core.live_channel_metadata import parse_categories_xml
from core.dynamic_review_category_policy import apply_dynamic_review_category_policy
from core.post_write_readback_guard_v066422 import validate_write_readback

C='<prestashop><categories><category><id>93</id><active>0</active><name><language id="1">Test</language><language id="2">Test</language></name></category></categories></prestashop>'
B='<prestashop><product><description><language id="1">Old EN</language><language id="2">Стар BG</language></description><associations><categories><category><id>18</id></category></categories><images><image><id>5</id></image></images><combinations><combination><id>10</id></combination></combinations></associations></product></prestashop>'
A='<prestashop><product><description><language id="1">English FAQ</language><language id="2">Български Често задавани въпроси</language></description><associations><categories><category><id>18</id></category><category><id>93</id></category></categories><images><image><id>5</id></image></images><combinations><combination><id>10</id></combination></combinations></associations></product></prestashop>'

class T(unittest.TestCase):
    def test_inactive_test_valid(self):
        r=parse_categories_xml(C,"Test",allow_inactive_review_category=True); self.assertTrue(r["ready"]); self.assertEqual(r["selected_category_id"],"93")
    def test_policy(self):
        r=parse_categories_xml(C,"Test",allow_inactive_review_category=True)
        p=apply_dynamic_review_category_policy(is_existing_product=True,existing_category_ids=["18"],category_discovery=r)
        self.assertEqual(p["write_category_ids"],["18","93"])
    def test_readback(self):
        r=validate_write_readback(before_xml=B,after_xml=A,language_mapping={"bg_id":"2","en_id":"1"},expected_review_category_id="93",expected_bg_markers=["Често задавани"],expected_en_markers=["FAQ"])
        self.assertTrue(r["passed"])
    def test_missing_category_blocks(self):
        r=validate_write_readback(before_xml=B,after_xml=A.replace('<category><id>93</id></category>',''),language_mapping={"bg_id":"2","en_id":"1"},expected_review_category_id="93")
        self.assertIn("REVIEW_CATEGORY_NOT_PERSISTED",r["blocking_flags"])
