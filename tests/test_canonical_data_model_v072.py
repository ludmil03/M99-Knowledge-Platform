from decimal import Decimal

import pytest

from core.catalog import (
    Channel,
    ChannelKind,
    ChannelPresence,
    ChannelProductGroup,
    ExternalIdentity,
    InventoryMapping,
    Market,
    Product,
    ProductGroup,
    ProductLifecycle,
    ProductVariant,
    PublicationStatus,
    SupplierOffer,
    require_hard_delete_confirmation,
    transition_product_lifecycle,
)


def test_product_group_defaults_to_draft():
    group = ProductGroup("M99-PG-000001", "Puma Safety Airtwist")
    assert group.lifecycle is ProductLifecycle.DRAFT


def test_product_belongs_to_product_group():
    product = Product("M99-P-000001", "M99-PG-000001", "Airtwist 2.0")
    assert product.product_group_id == "M99-PG-000001"


def test_variant_belongs_to_product_not_supplier():
    variant = ProductVariant("M99-V-000001", "M99-P-000001", "size-42")
    assert variant.product_id == "M99-P-000001"


def test_external_identity_is_mapping_not_master_id():
    ext = ExternalIdentity("dolibarr", "2045", "product")
    product = Product("M99-P-000001", "M99-PG-000001", "Airtwist", external_ids=[ext])
    assert product.m99_id == "M99-P-000001"
    assert product.external_ids[0].external_id == "2045"


def test_supplier_offer_maps_supplier_to_variant():
    offer = SupplierOffer(
        "M99-SO-000001",
        "M99-SUP-000001",
        "M99-V-000001",
        "PUMA-42",
        Decimal("72.50"),
        "eur",
        True,
    )
    assert offer.variant_id == "M99-V-000001"
    assert offer.currency == "EUR"


def test_supplier_offer_rejects_negative_price():
    with pytest.raises(ValueError):
        SupplierOffer(
            "M99-SO-000001",
            "M99-SUP-000001",
            "M99-V-000001",
            "SKU",
            Decimal("-1"),
        )


def test_market_is_not_channel():
    market = Market("bg", "Bulgaria", "BG", "BGN", "bg")
    channel = Channel("mela99", "mela99.com", market.code, ChannelKind.WEBSITE)
    assert market.code == "bg"
    assert channel.market_code == "bg"
    assert channel.code != market.code


def test_channel_product_group_controls_availability_without_deleting_group():
    mapping = ChannelProductGroup("mela99", "M99-PG-000001", enabled=False)
    assert mapping.enabled is False
    assert mapping.product_group_id == "M99-PG-000001"


def test_channel_presence_has_separate_publication_lifecycle():
    presence = ChannelPresence("mela99", "M99-V-000001")
    assert presence.publication_status is PublicationStatus.NOT_PUBLISHED


def test_inventory_mapping_references_external_erp_without_owning_stock():
    mapping = InventoryMapping("M99-V-000001", "dolibarr", "WH-1", "2045")
    assert mapping.system == "dolibarr"
    assert not hasattr(mapping, "quantity")


@pytest.mark.parametrize(
    "current,target",
    [
        (ProductLifecycle.DRAFT, ProductLifecycle.ACTIVE),
        (ProductLifecycle.ACTIVE, ProductLifecycle.PAUSED),
        (ProductLifecycle.PAUSED, ProductLifecycle.ACTIVE),
        (ProductLifecycle.ACTIVE, ProductLifecycle.RETIRED),
        (ProductLifecycle.PAUSED, ProductLifecycle.RETIRED),
    ],
)
def test_allowed_product_lifecycle_transitions(current, target):
    assert transition_product_lifecycle(current, target) is target


def test_retired_product_cannot_return_to_active():
    with pytest.raises(ValueError):
        transition_product_lifecycle(ProductLifecycle.RETIRED, ProductLifecycle.ACTIVE)


def test_hard_delete_requires_all_three_controls():
    assert require_hard_delete_confirmation(
        operator_approved=True,
        permission_granted=True,
        literal_confirmation="DELETE",
    )


@pytest.mark.parametrize(
    "approved,permission,literal,exc",
    [
        (False, True, "DELETE", PermissionError),
        (True, False, "DELETE", PermissionError),
        (True, True, "delete", ValueError),
    ],
)
def test_hard_delete_rejects_missing_control(approved, permission, literal, exc):
    with pytest.raises(exc):
        require_hard_delete_confirmation(
            operator_approved=approved,
            permission_granted=permission,
            literal_confirmation=literal,
        )
