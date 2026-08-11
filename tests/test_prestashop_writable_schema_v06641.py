import unittest
import xml.etree.ElementTree as ET

from core.prestashop_writable_schema import build_writable_product_snapshot, removed_top_level_fields
from core.s3s_master_content import build_s3s_content
from core.s3s_master_write_draft import mutate_master_to_review_draft

CURRENT = """<prestashop><product>
<id>2076</id><active>1</active><reference>MELA-REF</reference>
<manufacturer_name>Diadora</manufacturer_name><quantity>25</quantity><position_in_category>3</position_in_category>
<name><language id='1'>Старо име</language><language id='2'>Old name</language></name>
<link_rewrite><language id='1'>staro-ime</language><language id='2'>old-name</language></link_rewrite>
<meta_title><language id='1'>Old</language><language id='2'>Old</language></meta_title>
<meta_description><language id='1'>Old</language><language id='2'>Old</language></meta_description>
<description_short><language id='1'>Old</language><language id='2'>Old</language></description_short>
<description><language id='1'>Old</language><language id='2'>Old</language></description>
<associations><categories><category><id>12</id></category></categories><images><image><id>77</id></image></images><combinations><combination><id>100</id></combination></combinations></associations>
</product></prestashop>"""

BLANK = """<prestashop><product>
<id></id><active></active><reference></reference>
<name><language id='1'></language></name><link_rewrite><language id='1'></language></link_rewrite>
<meta_title><language id='1'></language></meta_title><meta_description><language id='1'></language></meta_description>
<description_short><language id='1'></language></description_short><description><language id='1'></language></description>
<associations><categories><category><id></id></category></categories><images><image><id></id></image></images><combinations><combination><id></id></combination></combinations></associations>
</product></prestashop>"""

FACTS={"model_name":"GLOVE A.BOX LOW PRO S3S","eu_sizes":[str(x) for x in range(35,49)],"anti_puncture":"K SOLE Ultralite","width":"11","technology":["A.Box System","Ariatex membrane"]}

class WritableSchemaV06641Tests(unittest.TestCase):
    def test_read_only_extra_fields_are_removed(self):
        writable=build_writable_product_snapshot(CURRENT,BLANK)
        removed=removed_top_level_fields(CURRENT,writable)
        self.assertIn("manufacturer_name",removed)
        self.assertIn("quantity",removed)
        self.assertIn("position_in_category",removed)
        self.assertNotIn("manufacturer_name",writable)

    def test_identity_and_associations_survive_filter(self):
        writable=build_writable_product_snapshot(CURRENT,BLANK)
        root=ET.fromstring(writable)
        self.assertEqual(root.findtext('.//id'),'2076')
        self.assertEqual(root.findtext('.//reference'),'MELA-REF')
        self.assertEqual(root.findtext('.//associations/images/image/id'),'77')
        self.assertEqual(root.findtext('.//associations/combinations/combination/id'),'100')

    def test_filtered_payload_can_be_mutated_to_review_draft(self):
        writable=build_writable_product_snapshot(CURRENT,BLANK)
        updated,meta=mutate_master_to_review_draft(writable,content=build_s3s_content(FACTS),review_category_id='938',change_name=False)
        root=ET.fromstring(updated)
        self.assertEqual(root.findtext('.//active'),'0')
        self.assertEqual([x.findtext('id') for x in root.findall('.//associations/categories/category')],['12','938'])
        self.assertEqual([x.text for x in root.findall('.//link_rewrite/language')],['staro-ime','old-name'])
        self.assertEqual([x.text for x in root.findall('.//name/language')],['Старо име','Old name'])

if __name__=='__main__': unittest.main()
