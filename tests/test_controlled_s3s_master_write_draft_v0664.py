import unittest
import xml.etree.ElementTree as ET

from core.review_category_policy import (
    apply_review_category_policy,
    publication_category_policy,
)
from core.s3s_master_content import build_s3s_content
from core.s3s_master_write_draft import mutate_master_to_review_draft


FACTS = {
    "model_name": "GLOVE A.BOX LOW PRO S3S",
    "eu_sizes": [str(x) for x in range(35,49)],
    "anti_puncture": "K SOLE Ultralite",
    "width": "11",
    "technology": ["A.Box System", "Ariatex membrane"],
}

XML = """<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
  <product>
    <id>2076</id>
    <active>1</active>
    <reference>MELA-REF</reference>
    <name>
      <language id="1">Старо име S3S</language>
      <language id="2">Old S3S name</language>
    </name>
    <link_rewrite>
      <language id="1">staro-s3s</language>
      <language id="2">old-s3s</language>
    </link_rewrite>
    <meta_title>
      <language id="1">Old meta title BG</language>
      <language id="2">Old meta title EN</language>
    </meta_title>
    <meta_description>
      <language id="1">Old meta BG</language>
      <language id="2">Old meta EN</language>
    </meta_description>
    <description_short>
      <language id="1">Old short BG</language>
      <language id="2">Old short EN</language>
    </description_short>
    <description>
      <language id="1">Old long BG</language>
      <language id="2">Old long EN</language>
    </description>
    <associations>
      <categories>
        <category><id>12</id></category>
        <category><id>44</id></category>
      </categories>
      <images><image><id>77</id></image></images>
      <combinations><combination><id>100</id></combination></combinations>
    </associations>
  </product>
</prestashop>
"""


class ControlledS3SMasterWriteDraftV0664Tests(unittest.TestCase):
    def test_existing_review_policy_keeps_old_categories_and_adds_938(self):
        p = apply_review_category_policy(
            is_existing_product=True,
            existing_category_ids=["12","44"],
        )
        self.assertEqual(p["write_category_ids"], ["12","44","938"])
        self.assertFalse(p["remove_original_categories"])

    def test_new_draft_uses_only_central_review_category(self):
        p = apply_review_category_policy(
            is_existing_product=False,
            existing_category_ids=[],
        )
        self.assertEqual(p["write_category_ids"], ["938"])
        self.assertEqual(p["mode"], "REVIEW_ONLY_FOR_NEW_DRAFT")

    def test_existing_publish_removes_only_review_category(self):
        p = publication_category_policy(
            is_existing_product=True,
            original_category_ids=["12","44","938"],
            approved_target_category_ids=None,
        )
        self.assertEqual(p["category_ids"], ["12","44"])

    def test_new_publish_blocks_without_operator_categories(self):
        p = publication_category_policy(
            is_existing_product=False,
            original_category_ids=[],
            approved_target_category_ids=[],
        )
        self.assertEqual(
            p["action"],
            "BLOCK_PUBLICATION_NO_APPROVED_TARGET_CATEGORY",
        )

    def test_master_update_keeps_name_slug_reference_and_categories(self):
        content = build_s3s_content(FACTS)
        xml, meta = mutate_master_to_review_draft(
            XML,
            content=content,
            review_category_id="938",
            change_name=False,
        )
        root = ET.fromstring(xml)
        self.assertEqual(root.findtext(".//active"), "0")
        self.assertEqual(root.findtext(".//reference"), "MELA-REF")
        names=[x.text for x in root.findall(".//name/language")]
        slugs=[x.text for x in root.findall(".//link_rewrite/language")]
        cats=[x.findtext("id") for x in root.findall(".//associations/categories/category")]
        self.assertEqual(names, ["Старо име S3S","Old S3S name"])
        self.assertEqual(slugs, ["staro-s3s","old-s3s"])
        self.assertEqual(cats, ["12","44","938"])
        self.assertFalse(meta["slug_changed"])

    def test_master_update_does_not_touch_images_or_combinations(self):
        content = build_s3s_content(FACTS)
        xml, _ = mutate_master_to_review_draft(
            XML,
            content=content,
            review_category_id="938",
            change_name=False,
        )
        root = ET.fromstring(xml)
        self.assertEqual(root.findtext(".//associations/images/image/id"), "77")
        self.assertEqual(root.findtext(".//associations/combinations/combination/id"), "100")

    def test_wrong_product_id_is_blocked(self):
        bad = XML.replace("<id>2076</id>", "<id>2100</id>", 1)
        with self.assertRaises(ValueError):
            mutate_master_to_review_draft(
                bad,
                content=build_s3s_content(FACTS),
                review_category_id="938",
                change_name=False,
            )

if __name__ == "__main__":
    unittest.main()
