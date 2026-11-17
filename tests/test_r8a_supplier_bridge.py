"""Actual native supplier shapes must survive the existing evidence adapter."""
from dataclasses import replace
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.services.supplier_evidence_adapters import from_bultex99
from app.services.supplier_evidence_runtime import normalize_supplier_evidence
from app.services.v073_phase45.bultex99_native_source_channel import NativeHydrated, NativeVariant
from integrations.bultex99_supplier.models import PublicProduct


def native_product():
    url = "https://bultex99.com/products/5161-uno-low"
    image = "https://bultex99.com/images/5161-black.jpg"
    variant = NativeVariant(
        "Observed black", "5161-black", url, image, "black",
        ({"size": "36", "supplier_reference": "06100764.36", "availability": "UNKNOWN"},),
    )
    return NativeHydrated(
        name="UNO LOW", url=url, source_key="5161", supplier_reference="06100764",
        calenda_product_id="5161", brand="Panda", price_text="58.90", currency="EUR",
        availability_text="UNKNOWN", description="Observed supplier description",
        images=(image,), variants=(variant,), warnings=("AVAILABILITY_UNPROVEN",),
        hydration_pass=True,
    )


def test_actual_native_hydration_preserves_identity_media_and_provenance():
    product = native_product()
    evidence = normalize_supplier_evidence("BULTEX99", product)
    assert evidence.validate() == ()
    assert evidence.source_key == "5161"
    assert evidence.source_url == product.url
    assert evidence.identity_facts["supplier_sku"].value == "06100764"
    assert evidence.identity_facts["supplier_reference"].value == "06100764"
    assert "manufacturer_mpn" not in evidence.identity_facts
    assert "calenda_product_id" not in evidence.commercial_evidence
    assert evidence.images[0].value == product.images[0]
    assert evidence.images[0].source == "BULTEX99_PUBLIC"
    assert evidence.images[0].source_url == product.url
    assert evidence.variants[0]["image_url"] == product.variants[0].image_url
    assert evidence.variants[0]["sizes"][0]["supplier_reference"] == "06100764.36"
    assert evidence.variants[0]["sizes"][0]["availability"] == "UNKNOWN"
    assert evidence.availability.value == "UNKNOWN"
    assert evidence.price.value == "58.90"
    assert evidence.commercial_evidence["currency"].value == "EUR"
    assert "price_basis" not in evidence.commercial_evidence
    assert evidence.technical_facts["description"].value == product.description
    assert evidence.warnings == product.warnings


def test_mapping_variants_are_preserved_without_aliasing_source():
    variant = {"code": "blue", "image_url": "https://bultex99.com/blue.jpg", "sizes": [{"size": "M"}]}
    product = replace(native_product(), variants=(variant,))
    evidence = from_bultex99(product)
    evidence.variants[0]["sizes"][0]["size"] = "L"
    assert variant["sizes"][0]["size"] == "M"


def test_historical_explicit_gross_contract_remains_supported():
    product = PublicProduct(
        "5161", "https://bultex99.com/product/5161", "UNO LOW",
        supplier_sku="06100764.36", gross_price_eur=Decimal("58.90"),
        availability="visible", brand="Panda", standard="Observed standard",
        legacy_stenso_refs=("OLD-1",),
    )
    evidence = from_bultex99(product)
    assert evidence.price.value == "58.90"
    assert evidence.commercial_evidence["currency"].value == "EUR"
    assert evidence.commercial_evidence["price_basis"].value == "GROSS"
    assert evidence.commercial_evidence["legacy_stenso_refs"].value == ("OLD-1",)
    assert evidence.images == () and evidence.variants == ()
    assert evidence.technical_facts["standard"].value == "Observed standard"


@pytest.mark.parametrize("raw", ["from 58.90", "58.90 EUR / 115.20 BGN", "1,234", "1.234,56", "NaN", "Infinity", "-5", "0"])
def test_ambiguous_or_invalid_price_is_retained_for_review_but_not_usable(raw):
    evidence = from_bultex99(replace(native_product(), price_text=raw))
    assert evidence.price is None
    assert evidence.commercial_evidence["price_text"].value == raw
    assert "PRICE_AMBIGUOUS_OR_INVALID" in evidence.warnings
    assert evidence.images and evidence.variants


def test_native_comma_decimal_uses_separate_observed_currency():
    evidence = from_bultex99(replace(native_product(), price_text="58,90", currency="BGN"))
    assert evidence.price.value == "58.90"
    assert evidence.commercial_evidence["currency"].value == "BGN"
    assert "price_basis" not in evidence.commercial_evidence


def test_price_without_currency_is_not_usable():
    evidence = from_bultex99(replace(native_product(), currency=""))
    assert evidence.price is None
    assert "PRICE_CURRENCY_NOT_PROVEN" in evidence.warnings


def test_unknown_variant_shape_does_not_become_fabricated_evidence():
    evidence = from_bultex99(replace(native_product(), variants=(SimpleNamespace(code="unknown"),)))
    assert evidence.variants == ()
    assert "VARIANT_SHAPE_UNSUPPORTED" in evidence.warnings
