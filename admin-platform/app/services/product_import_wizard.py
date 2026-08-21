from __future__ import annotations

from dataclasses import dataclass, field, asdict
from enum import StrEnum
from typing import Iterable


class SelectionMode(StrEnum):
    ONE_PRODUCT = "one_product"
    MULTIPLE_PRODUCTS = "multiple_products"
    ONE_CATEGORY = "one_category"
    MULTIPLE_CATEGORIES = "multiple_categories"
    ALL_PRODUCTS = "all_products"
    FIRST_N = "first_n"
    ONLY_NEW_TO_M99 = "only_new_to_m99"
    MANUAL_SELECTION = "manual_selection"


class WizardState(StrEnum):
    SOURCE = "source"
    SELECTION = "selection"
    IDENTITY = "identity"
    TARGETS = "targets"
    REVIEW = "review"
    READY_FOR_PREFLIGHT = "ready_for_preflight"


class ProposalStatus(StrEnum):
    PENDING_SUPER_ADMIN_APPROVAL = "PENDING_SUPER_ADMIN_APPROVAL"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    MERGED = "MERGED"


@dataclass(frozen=True)
class OrganizationOption:
    organization_id: str
    name: str
    roles: tuple[str, ...]
    approved: bool = True


@dataclass(frozen=True)
class TargetOption:
    key: str
    label: str
    kind: str
    authorized: bool
    ready: bool
    note: str = ""


@dataclass
class ImportWizardDraft:
    source_organization_id: str | None = None
    source_name: str | None = None
    selection_mode: str | None = None
    selected_product_refs: list[str] = field(default_factory=list)
    selected_category_refs: list[str] = field(default_factory=list)
    first_n: int | None = None
    identity_summary: str = "Identity review pending"
    requested_targets: list[str] = field(default_factory=list)
    authorized_targets: list[str] = field(default_factory=list)
    ready_targets: list[str] = field(default_factory=list)
    blocked_targets: list[str] = field(default_factory=list)
    current_state: str = WizardState.SOURCE.value

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


# Foundation registry. In later versions this comes from canonical DB / RBAC.
DEFAULT_ORGANIZATIONS: tuple[OrganizationOption, ...] = (
    OrganizationOption("org-stenso", "STENSO", ("SUPPLIER", "MANUFACTURER")),
    OrganizationOption("org-palltex", "PALLTEX", ("SUPPLIER", "MANUFACTURER")),
    OrganizationOption("org-bultex", "BULTEX", ("SUPPLIER",)),
)

# Foundation target registry. Authorization/ready states must later come from RBAC
# and live channel preflight. m99.eu is intentionally only one selectable target.
DEFAULT_TARGETS: tuple[TargetOption, ...] = (
    TargetOption("mela99.com", "mela99.com", "CHANNEL", True, True),
    TargetOption("rabotni-drehi.com", "rabotni-drehi.com", "CHANNEL", True, True),
    TargetOption("m99.eu", "m99.eu", "CHANNEL", True, True, "PrestaShop 9 adapter verified"),
    TargetOption("medicinski-drehi.com", "medicinski-drehi.com", "CHANNEL", True, True),
    TargetOption("laviro.ro", "laviro.ro", "CHANNEL", True, True),
    TargetOption("alviro.ro", "alviro.ro", "CHANNEL", True, False, "Requires channel readiness"),
    TargetOption("toplinka.com", "toplinka.com", "CHANNEL", False, False, "Not enabled for product import"),
    TargetOption("dolibarr", "Dolibarr ERP", "ERP", True, False, "Write contract not enabled in this foundation"),
)


def selection_modes() -> list[dict[str, str]]:
    return [
        {"value": SelectionMode.ONE_PRODUCT.value, "label": "Един продукт"},
        {"value": SelectionMode.MULTIPLE_PRODUCTS.value, "label": "Няколко продукта"},
        {"value": SelectionMode.ONE_CATEGORY.value, "label": "Една категория"},
        {"value": SelectionMode.MULTIPLE_CATEGORIES.value, "label": "Няколко категории"},
        {"value": SelectionMode.ALL_PRODUCTS.value, "label": "Всички продукти"},
        {"value": SelectionMode.FIRST_N.value, "label": "Първите N продукта"},
        {"value": SelectionMode.ONLY_NEW_TO_M99.value, "label": "Само новите за M99"},
        {"value": SelectionMode.MANUAL_SELECTION.value, "label": "Ръчен избор"},
    ]


def approved_organizations() -> list[OrganizationOption]:
    return [org for org in DEFAULT_ORGANIZATIONS if org.approved]


def propose_organization(name: str, roles: Iterable[str]) -> dict[str, object]:
    cleaned = name.strip()
    if not cleaned:
        raise ValueError("Името на организацията е задължително.")

    normalized_roles = sorted({r.strip().upper() for r in roles if r.strip()})
    allowed = {"SUPPLIER", "MANUFACTURER"}
    if not normalized_roles or any(r not in allowed for r in normalized_roles):
        raise ValueError("Избери поне една валидна роля: SUPPLIER и/или MANUFACTURER.")

    return {
        "name": cleaned,
        "roles": normalized_roles,
        "status": ProposalStatus.PENDING_SUPER_ADMIN_APPROVAL.value,
        "visible_to_operators": False,
        "message": "Предложението е изпратено за одобрение от Super Admin.",
    }


def available_targets() -> list[TargetOption]:
    return list(DEFAULT_TARGETS)


def resolve_target_scope(requested: Iterable[str]) -> dict[str, list[str]]:
    requested_unique = list(dict.fromkeys(x.strip() for x in requested if x.strip()))
    by_key = {t.key: t for t in DEFAULT_TARGETS}

    authorized: list[str] = []
    ready: list[str] = []
    blocked: list[str] = []

    for key in requested_unique:
        target = by_key.get(key)
        if target is None:
            blocked.append(key)
            continue
        if target.authorized:
            authorized.append(key)
        if target.authorized and target.ready:
            ready.append(key)
        else:
            blocked.append(key)

    return {
        "requested_targets": requested_unique,
        "authorized_targets": authorized,
        "ready_targets": ready,
        "blocked_targets": blocked,
    }


def validate_selection(mode: str, products: list[str], categories: list[str], first_n: int | None) -> None:
    valid = {m.value for m in SelectionMode}
    if mode not in valid:
        raise ValueError("Невалиден начин за избор.")

    if mode == SelectionMode.ONE_PRODUCT.value and len(products) != 1:
        raise ValueError("Избери точно един продукт.")

    if mode == SelectionMode.MULTIPLE_PRODUCTS.value and len(products) < 2:
        raise ValueError("Избери поне два продукта.")

    if mode == SelectionMode.ONE_CATEGORY.value and len(categories) != 1:
        raise ValueError("Избери точно една категория.")

    if mode == SelectionMode.MULTIPLE_CATEGORIES.value and len(categories) < 2:
        raise ValueError("Избери поне две категории.")

    if mode == SelectionMode.FIRST_N.value and (first_n is None or first_n <= 0):
        raise ValueError("Въведи положителен брой продукти.")


def build_review_summary(draft: ImportWizardDraft) -> dict[str, object]:
    selection_label = next(
        (x["label"] for x in selection_modes() if x["value"] == draft.selection_mode),
        "Не е избрано",
    )

    return {
        "source": draft.source_name or "Не е избран",
        "selection": selection_label,
        "products_count": len(draft.selected_product_refs),
        "categories_count": len(draft.selected_category_refs),
        "first_n": draft.first_n,
        "identity": draft.identity_summary,
        "requested_targets": draft.requested_targets,
        "ready_targets": draft.ready_targets,
        "blocked_targets": draft.blocked_targets,
        "can_continue": bool(draft.ready_targets),
        "write_performed": False,
    }
