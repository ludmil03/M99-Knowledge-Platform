import json
import unittest
from pathlib import Path

from core.internal_existing_product_discovery import discover_existing_product
from core.content_seo_preview import build_diadora_content_preview
from core.canonical_product_facts import build_canonical_product_facts, canonical_values
from integrations.catalog_discovery import (
    PrestaShopReadOnlyAdapter,
    WooCommerceReadOnlyAdapter,
)


class InternalExistingProductDiscoveryV065Tests(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(
            Path("tests/fixtures/internal_discovery_v065_sample.json").read_text(
                encoding="utf-8"
            )
        )
        source = json.loads(
            Path(
                "tests/fixtures/diadora_glove_abox_low_pro_s1ps_real.json"
            ).read_text(encoding="utf-8")
        )
        m = source["manufacturer_evidence"]
        canonical = build_canonical_product_facts(
            m["source_name"], m["source_url"], m["facts"]
        )
        self.facts = canonical_values(canonical)

    def test_exact_reference_is_existing(self):
        result = discover_existing_product(
            "mela99.com",
            self.fixture["canonical_product"],
            self.fixture["channels"]["mela99.com"],
        )
        self.assertEqual(result["decision"], "EXISTING")
        self.assertEqual(
            result["action"],
            "UPDATE_EXISTING_PRESERVE_ID_AND_URL",
        )
        self.assertTrue(result["preserve_existing_product_id"])
        self.assertTrue(result["preserve_existing_url"])
        self.assertEqual(result["selected_product_id"], "2045")
        self.assertEqual(
            result["selected_url"],
            "https://mela99.com/existing-diadora",
        )

    def test_empty_internal_catalog_is_new_candidate(self):
        result = discover_existing_product(
            "m99.eu",
            self.fixture["canonical_product"],
            self.fixture["channels"]["m99.eu"],
        )
        self.assertEqual(result["decision"], "NEW")
        self.assertEqual(result["action"], "CREATE_CANDIDATE")
        self.assertFalse(result["publish_allowed"])

    def test_exact_model_without_identifier_is_possible_duplicate(self):
        result = discover_existing_product(
            "rabotni-drehi.com",
            self.fixture["canonical_product"],
            self.fixture["channels"]["rabotni-drehi.com"],
        )
        self.assertEqual(result["decision"], "POSSIBLE_DUPLICATE")
        self.assertEqual(result["action"], "OPERATOR_REVIEW_BEFORE_CREATE")

    def test_exact_reference_with_class_conflict_is_conflict(self):
        result = discover_existing_product(
            "laviro.ro",
            self.fixture["canonical_product"],
            self.fixture["channels"]["laviro.ro"],
        )
        self.assertEqual(result["decision"], "CONFLICT")
        comparison = result["comparisons"][0]
        self.assertTrue(comparison["protection_class_conflict"])

    def test_legacy_identifier_in_reference_is_existing(self):
        identity = dict(self.fixture["canonical_product"])
        identity["legacy_identifiers"] = ["OLD-MW-7788"]
        candidate = [{
            "product_id": "300",
            "url": "/old-product",
            "name": "Old product title",
            "brand": None,
            "reference": "OLD-MW-7788",
            "ean": None,
            "legacy_identifiers": [],
            "protection_class": None,
            "active": True,
            "raw_source": "test",
        }]
        result = discover_existing_product("mela99.com", identity, candidate)
        self.assertEqual(result["decision"], "EXISTING")
        self.assertIn(
            "legacy_identifier",
            result["comparisons"][0]["matched_identity_keys"],
        )

    def test_adapters_expose_no_write_methods(self):
        forbidden = {
            "create", "update", "delete", "post", "put", "patch",
            "create_product", "update_product", "delete_product",
        }
        for cls in (PrestaShopReadOnlyAdapter, WooCommerceReadOnlyAdapter):
            names = {name.lower() for name in dir(cls)}
            self.assertFalse(forbidden & names)

    def test_meta_descriptions_are_channel_differentiated(self):
        content = build_diadora_content_preview(self.facts)
        bg = {
            content["mela99.com"]["bg"]["meta_description"],
            content["m99.eu"]["bg"]["meta_description"],
            content["rabotni-drehi.com"]["bg"]["meta_description"],
        }
        self.assertEqual(len(bg), 3)

    def test_faq_intent_differs_between_catalogue_and_transactional_site(self):
        content = build_diadora_content_preview(self.facts)
        mela = [
            x["q"] for x in content["mela99.com"]["bg"]["faq"]
        ]
        rabotni = [
            x["q"] for x in content["rabotni-drehi.com"]["bg"]["faq"]
        ]
        self.assertNotEqual(mela, rabotni)
        self.assertEqual(len(mela), 6)
        self.assertEqual(len(rabotni), 6)

    def test_public_search_is_not_internal_authority(self):
        # Architecture invariant: internal discovery uses candidates supplied by
        # the owned channel adapter, not search-engine results.
        result = discover_existing_product(
            "m99.eu",
            self.fixture["canonical_product"],
            [],
        )
        self.assertEqual(result["decision"], "NEW")
        self.assertTrue(result["operator_confirmation_required"])
        self.assertFalse(result["publish_allowed"])


if __name__ == "__main__":
    unittest.main()
