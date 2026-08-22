from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SupplierState:
    verification_ok: bool
    price: str | None
    availability: str | None
    variants: tuple[tuple[str, str], ...]
    discontinued: bool = False
    product_fingerprint: str | None = None


@dataclass(frozen=True)
class ChangeDecision:
    change_state: str
    changed_fields: tuple[str, ...]
    write_required: bool
    preserve_last_verified: bool = False


def compare_supplier_state(
    previous: SupplierState | None,
    current: SupplierState,
) -> ChangeDecision:
    if not current.verification_ok:
        return ChangeDecision(
            change_state="VERIFICATION_FAILED",
            changed_fields=(),
            write_required=False,
            preserve_last_verified=True,
        )

    if previous is None:
        return ChangeDecision(
            change_state="PRODUCT_CHANGED",
            changed_fields=("INITIAL_VERIFIED_OBSERVATION",),
            write_required=False,
        )

    if current.discontinued and not previous.discontinued:
        return ChangeDecision(
            change_state="SUPPLIER_DISCONTINUED",
            changed_fields=("discontinued",),
            write_required=True,
        )

    changed = []
    if current.price != previous.price:
        changed.append("price")
    if current.availability != previous.availability:
        changed.append("availability")
    if current.variants != previous.variants:
        changed.append("variant_availability")
    if current.product_fingerprint != previous.product_fingerprint:
        changed.append("product")

    if not changed:
        return ChangeDecision(
            change_state="NO_CHANGE",
            changed_fields=(),
            write_required=False,
        )

    if changed == ["price"]:
        state = "PRICE_CHANGED"
    elif changed == ["availability"]:
        state = "AVAILABILITY_CHANGED"
    elif changed == ["variant_availability"]:
        state = "VARIANT_AVAILABILITY_CHANGED"
    else:
        state = "PRODUCT_CHANGED"

    return ChangeDecision(
        change_state=state,
        changed_fields=tuple(changed),
        write_required=True,
    )


def filter_existing_write_targets(
    *,
    requested_existing_targets: list[str],
    presence_by_target: dict[str, str],
) -> tuple[list[str], list[str]]:
    """Daily sync writes only to already-existing mappings.

    Missing channels are returned as blocked/skipped and are never auto-created.
    """
    writable = []
    skipped = []
    present_states = {
        "PRESENT_DRAFT",
        "PRESENT_TEST",
        "PRESENT_ACTIVE",
        "PRESENT_PAUSED",
        "PRESENT_RETIRED",
        "PRESENT_LAST_VERIFIED",
    }

    for target in requested_existing_targets:
        if presence_by_target.get(target) in present_states:
            writable.append(target)
        else:
            skipped.append(target)

    return writable, skipped
