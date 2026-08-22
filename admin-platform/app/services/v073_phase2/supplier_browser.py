from __future__ import annotations

from datetime import datetime, timezone
import json

from sqlalchemy import select

from app.connectors.suppliers.registry import SupplierConnectorRegistry
from app.connectors.suppliers.stenso import StensoPublicConnector
from app.persistence.v073_phase2.database import make_session_factory
from app.persistence.v073_phase2.models import (
    Organization,
    SupplierObservation,
    SupplierSource,
    new_id,
)


def default_registry() -> SupplierConnectorRegistry:
    registry = SupplierConnectorRegistry()
    registry.register("stenso_public", StensoPublicConnector)
    return registry


def get_operator_source(database_url: str, source_id: str) -> dict:
    factory = make_session_factory(database_url)
    with factory() as session:
        source = session.scalar(
            select(SupplierSource).where(SupplierSource.id == source_id)
        )
        if source is None:
            raise ValueError("SupplierSource not found.")
        org = source.organization
        if org.status != "APPROVED" or not org.visible_to_operators:
            raise PermissionError("Supplier Organization is not operator-visible.")
        if source.status != "READY" or not source.operator_browsable:
            raise PermissionError("SupplierSource is not ready for operator browsing.")
        if not source.read_only:
            raise PermissionError("Supplier Browser source must be read-only.")

        return {
            "source_id": source.id,
            "organization_id": org.id,
            "organization_name": org.name,
            "label": source.label,
            "connector_key": source.connector_key,
            "source_type": source.source_type,
            "base_url": source.base_url,
            "capabilities": json.loads(source.capabilities_json),
            "catalog_roots": json.loads(source.catalog_roots_json),
            "read_only": source.read_only,
        }


def create_connector(database_url: str, source_id: str):
    config = get_operator_source(database_url, source_id)
    registry = default_registry()
    return registry.create(
        config["connector_key"],
        base_url=config["base_url"],
        catalog_roots=config["catalog_roots"],
    )


def live_categories(database_url: str, source_id: str) -> list[dict]:
    connector = create_connector(database_url, source_id)
    return [
        {
            "key": x.key,
            "name": x.name,
            "url": x.url,
            "product_count": x.product_count,
        }
        for x in connector.list_categories()
    ]


def live_products(
    database_url: str,
    source_id: str,
    category_key: str,
    *,
    page: int = 1,
    limit: int = 100,
) -> list[dict]:
    connector = create_connector(database_url, source_id)
    return [
        {
            "source_key": x.source_key,
            "name": x.name,
            "url": x.url,
            "price_text": x.price_text,
            "availability_text": x.availability_text,
            "image_url": x.image_url,
        }
        for x in connector.list_products(category_key, page=page, limit=limit)
    ]


def live_product(database_url: str, source_id: str, source_key: str) -> dict:
    connector = create_connector(database_url, source_id)
    x = connector.get_product(source_key)
    return {
        "source_key": x.source_key,
        "name": x.name,
        "url": x.url,
        "reference": x.reference,
        "mpn": x.mpn,
        "ean": x.ean,
        "price_text": x.price_text,
        "availability_text": x.availability_text,
        "images": list(x.images),
        "variants": list(x.variants),
        "facts": dict(x.facts),
    }


def persist_observation(
    database_url: str,
    *,
    source_id: str,
    source_key: str,
    source_url: str | None,
    payload: dict,
) -> str:
    factory = make_session_factory(database_url)
    with factory.begin() as session:
        obs = SupplierObservation(
            id=new_id("obs"),
            source_id=source_id,
            source_key=source_key,
            source_url=source_url,
            observed_at=datetime.now(timezone.utc),
            verified_at=datetime.now(timezone.utc),
            payload_json=json.dumps(payload, ensure_ascii=False),
            conflict_state="NONE",
        )
        session.add(obs)
        session.flush()
        return obs.id
