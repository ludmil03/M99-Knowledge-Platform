import unittest
from core.cherokee_canonical_merge_v0672 import compare_fact,build_canonical
class T(unittest.TestCase):
 def manufacturer(self):
  return {"authority":"AUTHORITATIVE","source_url":"m","official_images":[],"commercial_observation":{},
  "facts":{"brand":"Cherokee","collection":"WW Revolution","canonical_style":"WW601","manufacturer_item":"CK-WW601--",
  "official_name":"Women's 2-Pocket Sweetheart V-Neck Scrub Top","fit":"Missy relaxed fit",
  "center_back_length_inches":26,"neckline":"Curved V-neckline","sleeves":"Short sleeves",
  "pockets":"2 front patch pockets with instrument loops","mesh_side_panels":True,"shirttail_hem":True,
  "material":"78% polyester, 20% rayon, 2% spandex","fabric":"Silky stretch twill fabric"}}
 def stenso(self,material="78% polyester, 20% rayon, 2% spandex"):
  return {"source_url":"s","supplier_images":[],"commercial_observation":{"raw_price_observations":[],"availability":None},
  "identity":{"brand":"Cherokee","supplier_style_alias":"WWE601","target_colour":"NAVY / DARK BLUE","supplier_reference":"08001931"},
  "facts":{"material":material,"sizes_visible":["XS","S","M","L","XL","2XL"]}}
 def test_consensus(self): self.assertEqual(compare_fact("material","Cotton","cotton")["status"],"VERIFIED_CONSENSUS")
 def test_conflict(self): self.assertEqual(compare_fact("material","Cotton","Polyester")["status"],"SOURCE_CONFLICT")
 def test_alias_preserved(self): self.assertIn("WWE601",build_canonical(self.manufacturer(),self.stenso())["canonical_identity"]["supplier_style_aliases"])
 def test_no_auto_ids(self):
  x=build_canonical(self.manufacturer(),self.stenso());self.assertIsNone(x["m99_reference_proposed"]);self.assertIsNone(x["m99_productgroup_id_proposed"])
 def test_no_auto_price(self): self.assertIsNone(build_canonical(self.manufacturer(),self.stenso())["commercial"]["m99_selling_price"])
 def test_content_ready_when_no_conflict(self): self.assertTrue(build_canonical(self.manufacturer(),self.stenso())["content_evidence"]["ready"])
