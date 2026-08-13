import unittest
from core.cherokee_all_sites_publish_v06743 import build_all_sites_package,CHANNELS
class T(unittest.TestCase):
 def setUp(self):self.d=build_all_sites_package()
 def test_six_sites(self):self.assertEqual(len(self.d["publication_manifest"]),6)
 def test_all_sites_required(self):self.assertTrue(self.d["publication_policy"]["all_sites_required"])
 def test_partial_failure_forbidden(self):self.assertTrue(self.d["publication_policy"]["partial_success_is_failure"])
 def test_write_draft(self):
  for x in self.d["publication_manifest"].values():self.assertEqual(x["mode"],"WRITE_DRAFT");self.assertFalse(x["active_after_write"])
 def test_bg_channels(self):
  for s in ["mela99.com","m99.eu","rabotni-drehi.com","medicinski-drehi.com"]:self.assertEqual(CHANNELS[s]["languages"],["bg","en","ru"])
 def test_ro_channels(self):
  for s in ["laviro.ro","alviro.ro"]:self.assertEqual(CHANNELS[s]["languages"],["ro","en"])
 def test_channel_specific(self):
  a=self.d["channel_documents"]["mela99.com"]["bg"]["short_description"];b=self.d["channel_documents"]["m99.eu"]["bg"]["short_description"];self.assertNotEqual(a,b)
 def test_similarity_guard(self):self.assertTrue(self.d["similarity_guard"]["all_pass"])
 def test_unknown_adapters_block(self):
  self.assertEqual(self.d["publication_manifest"]["medicinski-drehi.com"]["adapter_status"],"BLOCKED_CONFIGURATION")
  self.assertEqual(self.d["publication_manifest"]["alviro.ro"]["adapter_status"],"BLOCKED_CONFIGURATION")
 def test_no_live_publish(self):self.assertFalse(self.d["publication_policy"]["live_publish_allowed"])
