import unittest
from core.internal_existing_product_discovery import discover_existing_product

IDENTITY = {
    "brand": "Diadora Utility",
    "model_name": "GLOVE A.BOX LOW PRO S3S",
    "manufacturer_item": "701.183119_80013",
    "ean": None,
    "legacy_identifiers": [],
    "protection_class": "S3S",
}

def candidate(name, ref="OLD-REF", protection=None):
    return [{
        "product_id": "999",
        "url": "https://mela99.com/example",
        "name": name,
        "brand": None,
        "reference": ref,
        "ean": None,
        "legacy_identifiers": [],
        "protection_class": protection,
        "active": True,
        "raw_source": "test",
    }]

class DiadoraS3SExistingProductV0662Tests(unittest.TestCase):
    def test_prefixed_existing_title_is_possible_duplicate(self):
        r = discover_existing_product(
            "mela99.com", IDENTITY,
            candidate("Работни обувки Diadora Glove A.Box Low Pro S3S"),
        )
        self.assertEqual(r["decision"], "POSSIBLE_DUPLICATE")
        self.assertFalse(r["publish_allowed"])

    def test_exact_reference_is_existing(self):
        r = discover_existing_product(
            "mela99.com", IDENTITY,
            candidate("Работни обувки Diadora Glove A.Box Low Pro S3S",
                      "701.183119_80013", "S3S"),
        )
        self.assertEqual(r["decision"], "EXISTING")

    def test_s1ps_remains_different_identity(self):
        r = discover_existing_product(
            "mela99.com", IDENTITY,
            candidate("Работни обувки Diadora Glove A.Box Low Pro S1PS",
                      "701.183121_80013", "S1PS"),
        )
        self.assertEqual(r["decision"], "NEW")

if __name__ == "__main__":
    unittest.main()
