import unittest

from core.duplicate_resolution import (
    rank_candidates,
    resolve_duplicates,
)
from core.product_snapshot_analysis import (
    summarize_product_xml,
    add_snapshot_quality,
)


COMPARISONS = [
    {
        "candidate": {
            "product_id": "2076",
            "url": "https://mela99.com/rabotni-obuvki-diadora-glove-a-box-low-pro-s3s",
            "name": "Работни обувки Diadora Glove A.Box Low Pro S3S",
            "brand": None,
            "reference": "MELA-REF",
            "ean": None,
            "legacy_identifiers": [],
            "protection_class": None,
            "active": True,
            "raw_source": "prestashop_webservice_get",
        },
        "decision": "POSSIBLE_DUPLICATE",
        "score": 60,
        "matched_identity_keys": [],
        "model_match": True,
        "brand_match": False,
        "protection_class_conflict": False,
        "reasons": ["normalized_model_family_match"],
    },
    {
        "candidate": {
            "product_id": "2100",
            "url": "https://mela99.com/--diadora-glove-abox-low-pro-s3s2",
            "name": "Работни обувки Diadora GLOVE A.BOX LOW PRO S3S 2.",
            "brand": None,
            "reference": None,
            "ean": None,
            "legacy_identifiers": [],
            "protection_class": None,
            "active": True,
            "raw_source": "prestashop_webservice_get",
        },
        "decision": "POSSIBLE_DUPLICATE",
        "score": 60,
        "matched_identity_keys": [],
        "model_match": True,
        "brand_match": False,
        "protection_class_conflict": False,
        "reasons": ["normalized_model_family_match"],
    },
    {
        "candidate": {
            "product_id": "2147",
            "url": "https://mela99.com/--diadora-glove-abox-low-pro-s3s-fo-sr-hro-esd",
            "name": "Работни обувки DIADORA GLOVE A.BOX LOW PRO S3S FO SR HRO ESD",
            "brand": None,
            "reference": None,
            "ean": None,
            "legacy_identifiers": [],
            "protection_class": None,
            "active": True,
            "raw_source": "prestashop_webservice_get",
        },
        "decision": "POSSIBLE_DUPLICATE",
        "score": 60,
        "matched_identity_keys": [],
        "model_match": True,
        "brand_match": False,
        "protection_class_conflict": False,
        "reasons": ["normalized_model_family_match"],
    },
]


XML = """<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
  <product>
    <id>2076</id>
    <active>1</active>
    <reference>MELA-REF</reference>
    <ean13></ean13>
    <price>120.000000</price>
    <id_category_default>938</id_category_default>
    <date_add>2024-01-01 10:00:00</date_add>
    <date_upd>2026-08-10 12:00:00</date_upd>
    <name>
      <language id="1">Работни обувки Diadora Glove A.Box Low Pro S3S</language>
      <language id="2">Diadora Glove A.Box Low Pro S3S</language>
    </name>
    <link_rewrite>
      <language id="1">rabotni-obuvki-diadora-glove-a-box-low-pro-s3s</language>
      <language id="2">diadora-glove-a-box-low-pro-s3s</language>
    </link_rewrite>
    <description_short>
      <language id="1">Кратко</language>
      <language id="2">Short</language>
    </description_short>
    <description>
      <language id="1">Описание</language>
      <language id="2">Description</language>
    </description>
    <associations>
      <categories><category><id>938</id></category></categories>
      <combinations>
        <combination><id>10</id></combination>
        <combination><id>11</id></combination>
      </combinations>
      <images><image><id>50</id></image></images>
    </associations>
  </product>
</prestashop>
"""


class DuplicateResolutionV0663Tests(unittest.TestCase):
    def test_2076_ranks_above_dirty_url_candidates(self):
        ranked = rank_candidates(COMPARISONS)
        self.assertEqual(ranked[0]["product_id"], "2076")
        self.assertTrue(ranked[0]["has_clean_url"])

    def test_no_auto_master_without_operator(self):
        result = resolve_duplicates(COMPARISONS)
        self.assertEqual(result["decision"], "REVIEW_REQUIRED")
        self.assertFalse(result["write_allowed"])
        self.assertIsNone(result["master"])

    def test_exact_confirmation_selects_master(self):
        result = resolve_duplicates(
            COMPARISONS,
            operator_master_product_id="2076",
            operator_confirmation="CONFIRM MASTER 2076 M99 100017 MELA99",
        )
        self.assertEqual(result["decision"], "MASTER_SELECTED")
        self.assertEqual(result["master"]["product_id"], "2076")
        self.assertEqual(result["master"]["identity_status"], "EXISTING_CONFIRMED")
        self.assertEqual(result["master"]["url_action"], "KEEP")
        self.assertEqual(result["master"]["product_name_action"], "KEEP_BY_DEFAULT")
        self.assertFalse(result["delete_allowed"])

    def test_bad_confirmation_is_blocked(self):
        with self.assertRaises(ValueError):
            resolve_duplicates(
                COMPARISONS,
                operator_master_product_id="2076",
                operator_confirmation="YES",
            )

    def test_duplicates_are_review_only_not_delete(self):
        result = resolve_duplicates(
            COMPARISONS,
            operator_master_product_id="2076",
            operator_confirmation="CONFIRM MASTER 2076 M99 100017 MELA99",
        )
        ids = {x["product_id"] for x in result["duplicates"]}
        self.assertEqual(ids, {"2100", "2147"})
        self.assertTrue(all(
            x["lifecycle_action"] == "DUPLICATE_REVIEW"
            for x in result["duplicates"]
        ))

    def test_snapshot_extracts_preservation_data(self):
        snapshot = summarize_product_xml(XML)
        self.assertEqual(snapshot["id"], "2076")
        self.assertEqual(snapshot["reference"], "MELA-REF")
        self.assertEqual(
            snapshot["slug_bg"],
            "rabotni-obuvki-diadora-glove-a-box-low-pro-s3s",
        )
        self.assertEqual(snapshot["combination_count"], 2)
        self.assertEqual(snapshot["image_count"], 1)

    def test_snapshot_quality_rewards_existing_assets(self):
        snapshot = add_snapshot_quality(summarize_product_xml(XML))
        self.assertGreaterEqual(snapshot["snapshot_quality_score"], 50)
        self.assertIn("HAS_COMBINATIONS", snapshot["snapshot_quality_reasons"])
        self.assertIn("HAS_IMAGES", snapshot["snapshot_quality_reasons"])


if __name__ == "__main__":
    unittest.main()
