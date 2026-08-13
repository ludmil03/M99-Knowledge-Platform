import unittest
from core.cherokee_all_sites_content_v06744 import CHANNEL_CONTENT
class T(unittest.TestCase):
 def test_all_six(self):self.assertEqual(len(CHANNEL_CONTENT),6)
 def test_mela_langs(self):self.assertEqual(set(CHANNEL_CONTENT["mela99.com"]),{"bg","en","ru"})
 def test_laviro_langs(self):self.assertEqual(set(CHANNEL_CONTENT["laviro.ro"]),{"ro","en"})
 def test_channel_different(self):self.assertNotEqual(CHANNEL_CONTENT["mela99.com"]["bg"]["short"],CHANNEL_CONTENT["m99.eu"]["bg"]["short"])
