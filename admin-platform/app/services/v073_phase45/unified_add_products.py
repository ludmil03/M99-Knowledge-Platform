from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.services.v073_phase45.source_registry_persistence import (
    ApprovedSourceRecord,
    CanonicalCategoryRecord,
)
from app.services.v073_phase45.palltex_public_connector import (
    PalltexPublicConnector,
    PalltexConnectorError,
)
from app.services.v073_phase45.calenda_public_connector import (
    CalendaPublicConnector,
    CalendaConnectorError,
)


@dataclass(frozen=True)
class SourceView:
    source_uuid: str
    source_kind: str
    name: str
    domain: str
    base_url: str
    activation_status: str


@dataclass(frozen=True)
class CategoryView:
    category_uuid: str
    name: str
    parent_uuid: str | None


@dataclass(frozen=True)
class ConnectorStatus:
    kind: str
    state: str
    message: str


class SourceDiscoveryError(RuntimeError):
    pass


def normalize_domain(value: str) -> str:
    value = (value or "").strip().lower()
    if "://" not in value:
        value = "https://" + value
    host = (urlparse(value).hostname or "").lower()
    return host[4:] if host.startswith("www.") else host


def approved_sources(db: Session, *, kind: str | None = None) -> list[SourceView]:
    q = db.query(ApprovedSourceRecord)
    if kind:
        q = q.filter(ApprovedSourceRecord.source_kind == kind.upper())
    rows = q.order_by(ApprovedSourceRecord.name.asc()).all()
    return [
        SourceView(
            str(r.source_uuid),
            str(r.source_kind),
            str(r.name),
            str(r.domain),
            str(r.base_url),
            str(r.activation_status),
        )
        for r in rows
        if str(r.activation_status).upper() == "ACTIVE"
    ]


def approved_categories(db: Session) -> list[CategoryView]:
    rows = (
        db.query(CanonicalCategoryRecord)
        .filter(CanonicalCategoryRecord.active.is_(True))
        .order_by(CanonicalCategoryRecord.name.asc())
        .all()
    )
    return [
        CategoryView(
            str(r.category_uuid),
            str(r.name),
            str(r.parent_uuid) if r.parent_uuid else None,
        )
        for r in rows
    ]


def require_source(db: Session, source_uuid: str) -> SourceView:
    r = (
        db.query(ApprovedSourceRecord)
        .filter(ApprovedSourceRecord.source_uuid == source_uuid)
        .first()
    )
    if r is None:
        raise SourceDiscoveryError("Approved source not found.")
    if str(r.activation_status).upper() != "ACTIVE":
        raise SourceDiscoveryError("Source is not ACTIVE.")
    return SourceView(
        str(r.source_uuid),
        str(r.source_kind),
        str(r.name),
        str(r.domain),
        str(r.base_url),
        str(r.activation_status),
    )


def connector_status(source: SourceView) -> ConnectorStatus:
    domain = normalize_domain(source.domain or source.base_url)
    if domain == "calenda.bg":
        return ConnectorStatus(
            "CALENDA_PUBLIC",
            "READY",
            "Calenda source-specific connector",
        )
    if domain == "palltex.bg":
        return ConnectorStatus(
            "PALLTEX_PUBLIC",
            "READY",
            "Palltex source-specific connector",
        )
    if domain == "stenso.net":
        return ConnectorStatus(
            "STENSO_REFERENCE",
            "READY",
            "Existing proven STENSO connector/runtime",
        )
    return ConnectorStatus(
        "GENERIC",
        "NOT_CONFIGURED",
        "No validated source-specific connector yet.",
    )


def list_source_categories(source: SourceView):
    domain = normalize_domain(source.domain or source.base_url)
    if domain == "calenda.bg":
        try:
            return CalendaPublicConnector(source.base_url).list_categories()
        except CalendaConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    if domain == "palltex.bg":
        try:
            return PalltexPublicConnector(source.base_url).list_categories()
        except PalltexConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    raise SourceDiscoveryError(
        f"No Add Products category connector registered for {domain}."
    )


def list_category_products(source: SourceView, category_url: str):
    if normalize_domain(category_url) != normalize_domain(source.domain or source.base_url):
        raise SourceDiscoveryError("Cross-domain category blocked.")

    domain = normalize_domain(source.domain or source.base_url)
    if domain == "calenda.bg":
        try:
            return CalendaPublicConnector(source.base_url).list_products(category_url)
        except CalendaConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    if domain == "palltex.bg":
        try:
            return PalltexPublicConnector(source.base_url).list_products(category_url)
        except PalltexConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    raise SourceDiscoveryError(
        f"No list_products connector registered for {domain}."
    )


def hydrate_product(source: SourceView, product_url: str):
    if normalize_domain(product_url) != normalize_domain(source.domain or source.base_url):
        raise SourceDiscoveryError("Cross-domain product blocked.")

    domain = normalize_domain(source.domain or source.base_url)
    if domain == "calenda.bg":
        try:
            return CalendaPublicConnector(source.base_url).get_product(product_url)
        except CalendaConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    if domain == "palltex.bg":
        try:
            return PalltexPublicConnector(source.base_url).get_product(product_url)
        except PalltexConnectorError as exc:
            raise SourceDiscoveryError(str(exc)) from exc
    raise SourceDiscoveryError(
        f"No get_product connector registered for {domain}."
    )


# Phase 4.3 R1/R2 compatibility API — preserved intentionally.
VALID_SELECTION_MODES = {
    "ONE_PRODUCT",
    "MULTIPLE_PRODUCTS",
    "ONE_CATEGORY",
    "MULTIPLE_CATEGORIES",
    "ALL_PRODUCTS",
}


def validate_selection(mode: str, selected_urls: list[str], source: SourceView):
    mode = str(mode or "").upper()
    if mode not in VALID_SELECTION_MODES:
        raise ValueError("Invalid selection mode.")

    source_domain = normalize_domain(source.domain or source.base_url)
    clean = []
    for url in selected_urls or []:
        if normalize_domain(url) != source_domain:
            raise ValueError("Selection contains URL outside approved source domain.")
        if url not in clean:
            clean.append(url)

    if mode == "ONE_PRODUCT" and len(clean) != 1:
        raise ValueError("ONE_PRODUCT requires exactly one selected product.")
    if mode == "MULTIPLE_PRODUCTS" and not clean:
        raise ValueError("MULTIPLE_PRODUCTS requires at least one selected product.")
    if mode == "ONE_CATEGORY" and len(clean) != 1:
        raise ValueError("ONE_CATEGORY requires exactly one selected category.")
    if mode == "MULTIPLE_CATEGORIES" and not clean:
        raise ValueError("MULTIPLE_CATEGORIES requires at least one selected category.")
    if mode == "ALL_PRODUCTS":
        clean = [source.base_url]

    return mode, tuple(clean)


def _classify(url: str, label: str = ""):
    path = (urlparse(url).path or "").lower()
    text = (label or "").strip().lower()

    category_tokens = ("/category/", "/categories/", "/cat/", "/catalog/")
    product_tokens = ("/product/", "/products/", "/produkt/", "/p/")

    if any(token in path for token in category_tokens):
        return "category", "path"
    if any(token in path for token in product_tokens):
        return "product", "path"
    if any(
        word in text
        for word in ("категория", "category", "работни обувки", "облекло")
    ):
        return "category", "label"
    return "unknown", "unclassified"
