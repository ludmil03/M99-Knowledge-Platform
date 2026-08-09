import csv
import tempfile
import unittest
from pathlib import Path

from integrations.dolibarr.product_exporter import (
    DOLIBARR_PRODUCT_HEADERS,
    DolibarrProductExporter,
)

ROOT = Path(__file__).resolve().parent.parent


class DolibarrProductExporterTests(unittest.TestCase):

    def setUp(self):
        self.exporter = DolibarrProductExporter(ROOT)

    def test_contract_is_44_columns(self):
        self.assertEqual(len(DOLIBARR_PRODUCT_HEADERS), 44)

    def test_velocity_exports_nine_variants(self):
        rows = self.exporter.build_rows("M99-PM-000001")
        self.assertEqual(len(rows), 9)
        self.assertEqual(rows[0]["p.ref"], "M99-PV-000001")
        self.assertEqual(rows[-1]["p.ref"], "M99-PV-000009")

    def test_required_fields(self):
        rows = self.exporter.build_rows("M99-PM-000001")
        self.assertEqual(self.exporter.validate_required(rows), [])

    def test_pmp_is_never_null_for_new_products(self):
        rows = self.exporter.build_rows("M99-PM-000001")
        self.assertTrue(all(row["p.pmp"] == 0 for row in rows))
        self.assertTrue(all(row["p.pmp"] is not None for row in rows))

    def test_csv_row_width(self):
        rows = self.exporter.build_rows("M99-PM-000001")
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "test.csv"
            self.exporter.export_csv(rows, path)
            with path.open("r", encoding="utf-8-sig", newline="") as f:
                parsed = list(csv.reader(f))
        self.assertTrue(all(len(row) == 44 for row in parsed))


if __name__ == "__main__":
    unittest.main()
