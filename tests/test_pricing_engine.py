import unittest
from decimal import Decimal
from core.pricing_engine import PricingInput, PricingStatus, calculate_price

class T(unittest.TestCase):
    def test_minus_1_5(self):
        r=calculate_price(PricingInput(Decimal("206.34"),Decimal("100"),Decimal("120")))
        self.assertEqual(str(r["target"]),"203.24")
        self.assertEqual(r["status"],PricingStatus.AUTO_APPROVED)

    def test_floor(self):
        r=calculate_price(PricingInput(Decimal("100"),Decimal("120"),Decimal("110")))
        self.assertEqual(str(r["final"]),"120.00")
