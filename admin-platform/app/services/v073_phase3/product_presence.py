from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select

from app.persistence.v073_phase3.database import make_session_factory
from app.persistence.v073_phase3.models import PRESENCE_STATES, ProductPresence, new_id


def upsert_presence(
    database_url: str,
    *,
    m99_product_id: str,
    target_key: str,
    target_type: str,
    presence_status: str,
    external_product_id: str | None = None,
    external_url: str | None = None,
    publication_state: str | None = None,
    price: str | None = None,
    currency: str | None = None,
    stock_representation: str | None = None,
    verified: bool = False,
    last_error: str | None = None,
) -> dict:
    if presence_status not in PRESENCE_STATES:
        raise ValueError(f"Invalid presence state: {presence_status}")

    factory = make_session_factory(database_url)
    with factory.begin() as session:
        row = session.scalar(
            select(ProductPresence).where(
                ProductPresence.m99_product_id == m99_product_id,
                ProductPresence.target_key == target_key,
            )
        )
        if row is None:
            row = ProductPresence(
                id=new_id("presence"),
                m99_product_id=m99_product_id,
                target_key=target_key,
                target_type=target_type,
            )
            session.add(row)

        # Failure never destroys last verified PRESENT truth.
        if presence_status == "VERIFICATION_FAILED" and row.last_verified_at is not None:
            row.presence_status = "PRESENT_LAST_VERIFIED"
            row.last_error = last_error or "VERIFICATION_FAILED"
        else:
            row.presence_status = presence_status
            row.last_error = last_error

        if external_product_id is not None:
            row.external_product_id = external_product_id
        if external_url is not None:
            row.external_url = external_url
        if publication_state is not None:
            row.publication_state = publication_state
        if price is not None:
            row.price = price
        if currency is not None:
            row.currency = currency
        if stock_representation is not None:
            row.stock_representation = stock_representation

        if verified:
            row.last_verified_at = datetime.now(timezone.utc)
            row.readback_status = "PASS"

        session.flush()
        return serialize_presence(row)


def serialize_presence(row: ProductPresence) -> dict:
    return {
        "m99_product_id": row.m99_product_id,
        "target_key": row.target_key,
        "target_type": row.target_type,
        "external_product_id": row.external_product_id,
        "external_url": row.external_url,
        "presence_status": row.presence_status,
        "publication_state": row.publication_state,
        "price": row.price,
        "currency": row.currency,
        "stock_representation": row.stock_representation,
        "last_verified_at": row.last_verified_at.isoformat() if row.last_verified_at else None,
        "last_sync_at": row.last_sync_at.isoformat() if row.last_sync_at else None,
        "sync_enabled": row.sync_enabled,
        "readback_status": row.readback_status,
        "front_office_verified": row.front_office_verified,
        "last_error": row.last_error,
    }


def product_to_targets(database_url: str, m99_product_id: str) -> list[dict]:
    factory = make_session_factory(database_url)
    with factory() as session:
        rows = session.scalars(
            select(ProductPresence)
            .where(ProductPresence.m99_product_id == m99_product_id)
            .order_by(ProductPresence.target_key)
        ).all()
        return [serialize_presence(row) for row in rows]


def target_to_products(database_url: str, target_key: str) -> list[dict]:
    factory = make_session_factory(database_url)
    with factory() as session:
        rows = session.scalars(
            select(ProductPresence)
            .where(ProductPresence.target_key == target_key)
            .order_by(ProductPresence.m99_product_id)
        ).all()
        return [serialize_presence(row) for row in rows]


def missing_in_targets(
    database_url: str,
    *,
    canonical_product_ids: list[str],
    target_keys: list[str],
) -> list[dict]:
    factory = make_session_factory(database_url)
    with factory() as session:
        existing = session.scalars(
            select(ProductPresence).where(
                ProductPresence.m99_product_id.in_(canonical_product_ids),
                ProductPresence.target_key.in_(target_keys),
            )
        ).all()
        index = {(x.m99_product_id, x.target_key): x.presence_status for x in existing}

    result = []
    for product_id in canonical_product_ids:
        missing = [
            target
            for target in target_keys
            if index.get((product_id, target), "NOT_PRESENT") == "NOT_PRESENT"
        ]
        if missing:
            result.append({"m99_product_id": product_id, "missing_targets": missing})
    return result
