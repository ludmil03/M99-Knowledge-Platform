import unittest
from pathlib import Path
from integrations.bultex_b2b.parser import parse_product_page

class T(unittest.TestCase):
    def test_parse(self):
        html=Path("tests/fixtures/bultex_product_sample.html").read_text(encoding="utf-8")
        o=parse_product_page(html,"x","222","Радиново")
        self.assertEqual(o.supplier_product_id,"109168")
        self.assertEqual(o.supplier_variant_code,"06200368.39")
        self.assertEqual(str(o.purchase_price_ex_vat),"23.24")
        self.assertEqual(str(o.recommended_price_ex_vat),"37.08")
        self.assertEqual(str(o.warehouse_stock.quantity),"45")
        self.assertEqual(o.barcode,"2006200368030")
