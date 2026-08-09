import unittest
from pathlib import Path

from core.moneywork_parser import MoneyWorkParser
from core.counterparty_normalizer import normalize_moneywork_counterparty
from core.counterparty_matcher import CounterpartyMatcher

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "tests" / "fixtures"


class MoneyWorkMigrationTests(unittest.TestCase):

    def test_article_fixed_width(self):
        parser = MoneyWorkParser()
        rows = parser.parse_articles(FIXTURES / "ARTDATA_sample.txt")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].legacy_code, "01001000001")
        self.assertEqual(rows[0].supplier_name, "TEST SUPPLIER")

    def test_supplier_wrapper(self):
        parser = MoneyWorkParser()
        rows = parser.parse_counterparties(
            FIXTURES / "suppliers_sample.csv",
            expected_role="S",
        )
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].vat_id, "BG123456789")

    def test_same_legal_entity_can_have_two_roles(self):
        parser = MoneyWorkParser()
        s = normalize_moneywork_counterparty(
            parser.parse_counterparties(
                FIXTURES / "suppliers_sample.csv",
                expected_role="S",
            )[0]
        )
        c = normalize_moneywork_counterparty(
            parser.parse_counterparties(
                FIXTURES / "customers_sample.csv",
                expected_role="K",
            )[0]
        )
        clusters = CounterpartyMatcher().cluster([s, c])
        self.assertEqual(len(clusters), 1)
        self.assertEqual(clusters[0].roles, {"SUPPLIER", "CUSTOMER"})


if __name__ == "__main__":
    unittest.main()
