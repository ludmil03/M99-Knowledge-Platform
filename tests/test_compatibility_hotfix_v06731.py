import unittest
from core.cherokee_canonical_merge_v0672 import compare_fact, build_canonical

class CompatibilityHotfixV06731Tests(unittest.TestCase):
    def manufacturer(self):
        return {
            "authority": "AUTHORITATIVE",
            "facts": {
                "brand": "Cherokee",
                "collection": "WW Revolution",
                "canonical_style": "WW601",
                "manufacturer_item": "CK-WW601--",
                "official_name": "Women's 2-Pocket Sweetheart V-Neck Scrub Top",
                "fit": "Missy relaxed fit",
                "center_back_length_inches": 26,
                "neckline": "Curved V-neckline",
                "sleeves": "Short sleeves",
                "pockets": "2 front patch pockets with instrument loops",
                "mesh_side_panels": True,
                "shirttail_hem": True,
                "material": "78% polyester, 20% rayon, 2% spandex",
                "fabric": "Silky stretch twill fabric",
            },
            "commercial_observation": {},
        }

    def stenso(self):
        return {
            "source_url": "https://stenso.net/test",
            "identity": {
                "supplier_style_alias": "WWE601",
                "supplier_reference": "08001931",
            },
            "facts": {
                "material": "78% polyester, 20% rayon, 2% spandex",
                "sizes_visible": ["XS", "S", "M", "L", "XL", "2XL"],
            },
            "commercial_observation": {
                "raw_price_observations": [],
                "availability": None,
            },
        }

    def test_compare_fact_api_restored(self):
        self.assertEqual(compare_fact("material", "Cotton", "cotton")["status"], "VERIFIED_CONSENSUS")

    def test_compare_fact_conflict_preserved(self):
        self.assertEqual(compare_fact("material", "Cotton", "Polyester")["status"], "SOURCE_CONFLICT")

    def test_build_canonical_api_restored(self):
        result = build_canonical(self.manufacturer(), self.stenso())
        self.assertEqual(result["identity_status"], "CANONICAL_READY")

    def test_supplier_alias_preserved(self):
        result = build_canonical(self.manufacturer(), self.stenso())
        self.assertIn("WWE601", result["canonical_identity"]["supplier_style_aliases"])

    def test_no_auto_price(self):
        result = build_canonical(self.manufacturer(), self.stenso())
        self.assertIsNone(result["commercial"]["m99_selling_price"])

    def test_no_auto_reference(self):
        result = build_canonical(self.manufacturer(), self.stenso())
        self.assertIsNone(result["m99_reference_proposed"])

    def test_write_stays_blocked(self):
        result = build_canonical(self.manufacturer(), self.stenso())
        self.assertFalse(result["write_allowed"])
