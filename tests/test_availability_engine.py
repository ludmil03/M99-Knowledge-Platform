import unittest
from core.availability_engine import AvailabilityStatus, decide_availability

class T(unittest.TestCase):
    def test_supplier_stock(self):
        s,label,sell=decide_availability(0,45)
        self.assertEqual(s,AvailabilityStatus.SUPPLIER_STOCK)
        self.assertTrue(sell)
