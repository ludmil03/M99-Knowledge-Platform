import os
import unittest
import xml.etree.ElementTree as ET

from core.controlled_publish_policy import (
    PublishMode,
    PublishAction,
    ExistingChannelIdentity,
    NameChangeProposal,
    decide_name_action,
    build_identity_lock,
    required_confirmation,
    validate_publish_gates,
)
from core.mela99_publish_payload import (
    PublishDocument,
    build_create_product_xml,
    mutate_existing_product_xml,
)


EXISTING_XML = """<?xml version="1.0" encoding="UTF-8"?>
<prestashop>
  <product>
    <id>2045</id>
    <active>1</active>
    <reference>OLD-MW-001</reference>
    <price>99.000000</price>
    <name>
      <language id="1">Старо име</language>
      <language id="2">Old name</language>
    </name>
    <link_rewrite>
      <language id="1">staro-ime</language>
      <language id="2">old-name</language>
    </link_rewrite>
    <meta_title>
      <language id="1">Старо SEO</language>
      <language id="2">Old SEO</language>
    </meta_title>
    <meta_description>
      <language id="1">Старо meta</language>
      <language id="2">Old meta</language>
    </meta_description>
    <description_short>
      <language id="1">Старо кратко</language>
      <language id="2">Old short</language>
    </description_short>
    <description>
      <language id="1">Старо описание</language>
      <language id="2">Old description</language>
    </description>
  </product>
</prestashop>
"""


def doc(active=False, price=None):
    return PublishDocument(
        name_bg="Ново доказано име",
        name_en="New proven name",
        short_bg="Ново кратко",
        short_en="New short",
        long_bg="Ново описание",
        long_en="New description",
        meta_title_bg="Ново SEO",
        meta_title_en="New SEO",
        meta_description_bg="Ново meta",
        meta_description_en="New meta",
        reference="701.183121_80013",
        category_id=938,
        active=active,
        price_ex_vat=price,
    )


class ControlledPublishV066Tests(unittest.TestCase):

    def test_existing_name_kept_without_operator_approval(self):
        existing = ExistingChannelIdentity(
            product_id="2045",
            product_name="Старо име",
            slug="staro-ime",
            url="https://mela99.com/staro-ime",
            legacy_identifiers=["OLD-MW-001"],
        )
        proposal = NameChangeProposal(
            current_name="Старо име",
            proposed_name="Ново доказано име",
            evidence_status="PROVEN_BETTER",
            operator_approved=False,
        )
        result = decide_name_action(existing, proposal)
        self.assertEqual(result["action"], "KEEP")
        self.assertEqual(result["name_to_write"], "Старо име")

    def test_existing_name_can_change_only_with_proof_and_operator(self):
        existing = ExistingChannelIdentity(
            product_id="2045",
            product_name="Старо име",
            slug="staro-ime",
            url="https://mela99.com/staro-ime",
            legacy_identifiers=["OLD-MW-001"],
        )
        proposal = NameChangeProposal(
            current_name="Старо име",
            proposed_name="Ново доказано име",
            evidence_status="PROVEN_BETTER",
            operator_approved=True,
        )
        result = decide_name_action(existing, proposal)
        self.assertEqual(result["action"], "CHANGE_APPROVED")
        self.assertEqual(result["name_to_write"], "Ново доказано име")

    def test_identity_lock_preserves_url_slug_and_legacy(self):
        existing = ExistingChannelIdentity(
            product_id="2045",
            product_name="Старо име",
            slug="staro-ime",
            url="https://mela99.com/staro-ime",
            legacy_identifiers=["OLD-MW-001"],
        )
        lock = build_identity_lock(existing, {"action":"KEEP","name_to_write":"Старо име"})
        self.assertTrue(lock["url_locked"])
        self.assertTrue(lock["slug_locked"])
        self.assertEqual(lock["product_id"], "2045")
        self.assertEqual(lock["legacy_identifiers"], ["OLD-MW-001"])

    def test_update_mutation_preserves_link_rewrite_and_reference(self):
        xml = mutate_existing_product_xml(EXISTING_XML, doc(), change_name=False)
        root = ET.fromstring(xml)
        slugs = [x.text for x in root.findall(".//link_rewrite/language")]
        self.assertEqual(slugs, ["staro-ime", "old-name"])
        self.assertEqual(root.findtext(".//reference"), "OLD-MW-001")

    def test_update_mutation_keeps_name_by_default(self):
        xml = mutate_existing_product_xml(EXISTING_XML, doc(), change_name=False)
        root = ET.fromstring(xml)
        names = [x.text for x in root.findall(".//name/language")]
        self.assertEqual(names, ["Старо име", "Old name"])

    def test_update_mutation_can_change_name_but_not_url(self):
        xml = mutate_existing_product_xml(EXISTING_XML, doc(), change_name=True)
        root = ET.fromstring(xml)
        names = [x.text for x in root.findall(".//name/language")]
        slugs = [x.text for x in root.findall(".//link_rewrite/language")]
        self.assertEqual(names, ["Ново доказано име", "New proven name"])
        self.assertEqual(slugs, ["staro-ime", "old-name"])

    def test_live_requires_pricing_and_availability(self):
        failures = validate_publish_gates({
            "single_product_scope": True,
            "target_channel_is_mela99": True,
            "content_ready": True,
            "internal_discovery_complete": True,
            "operator_approved": True,
            "audit_enabled": True,
            "rollback_enabled": True,
            "pricing_approved": False,
            "availability_approved": False,
            "publish_mode": "PUBLISH_LIVE",
        })
        self.assertIn("GATE_FAILED:pricing_approved", failures)
        self.assertIn("GATE_FAILED:availability_approved", failures)

    def test_confirmation_is_exact_and_product_scoped(self):
        self.assertEqual(
            required_confirmation(PublishMode.WRITE_DRAFT, PublishAction.UPDATE),
            "WRITE_DRAFT UPDATE M99 100002 MELA99",
        )

    def test_create_is_inactive_in_write_draft(self):
        xml = build_create_product_xml(
            doc(active=False),
            "rabotni-obuvki-diadora-glove-abox-low-pro-s1ps",
            "diadora-glove-abox-low-pro-s1ps-safety-shoes",
        )
        root = ET.fromstring(xml)
        self.assertEqual(root.findtext(".//active"), "0")
        self.assertEqual(root.findtext(".//id_category_default"), "938")

    def test_update_price_unchanged_when_price_not_approved(self):
        xml = mutate_existing_product_xml(EXISTING_XML, doc(price=None), change_name=False)
        root = ET.fromstring(xml)
        self.assertEqual(root.findtext(".//price"), "99.000000")


if __name__ == "__main__":
    unittest.main()
