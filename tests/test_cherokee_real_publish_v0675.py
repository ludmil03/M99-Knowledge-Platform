import unittest
from decimal import Decimal
from core.cherokee_real_publish_v0675 import calculate_bgn,REQUIRED,SKIPPED,CONFIRM
class T(unittest.TestCase):
 def test_price(self): self.assertEqual(calculate_bgn(Decimal('25.20')),Decimal('48.65'))
 def test_m99_excluded(self): self.assertNotIn('m99.eu',REQUIRED); self.assertEqual(SKIPPED,'m99.eu')
 def test_five_required(self): self.assertEqual(len(REQUIRED),5)
 def test_draft_confirmation(self): self.assertIn('PUBLISH_DRAFT',CONFIRM)
if __name__=='__main__': unittest.main()
