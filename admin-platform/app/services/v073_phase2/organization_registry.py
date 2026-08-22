from __future__ import annotations

from datetime import datetime, timezone
import json

from sqlalchemy import select

from app.persistence.v073_phase2.database import make_session_factory
from app.persistence.v073_phase2.models import (
    Organization,
    OrganizationRole,
    SupplierSource,
    new_id,
)

APPROVED = "APPROVED"
PENDING = "PENDING_SUPER_ADMIN_APPROVAL"
ALLOWED_ROLES = {"SUPPLIER", "MANUFACTURER"}


def propose_organization(
    database_url: str,
    *,
    name: str,
    roles: list[str],
    created_by: str,
) -> dict:
    cleaned = name.strip()
    normalized = sorted({r.strip().upper() for r in roles if r.strip()})

    if not cleaned:
        raise ValueError("Organization name is required.")
    if not normalized or any(r not in ALLOWED_ROLES for r in normalized):
        raise ValueError("Valid SUPPLIER and/or MANUFACTURER role is required.")

    factory = make_session_factory(database_url)
    with factory.begin() as session:
        existing = session.scalar(
            select(Organization).where(Organization.name.ilike(cleaned))
        )
        if existing:
            return {
                "organization_id": existing.id,
                "name": existing.name,
                "status": existing.status,
                "visible_to_operators": existing.visible_to_operators,
                "duplicate": True,
            }

        org = Organization(
            id=new_id("org"),
            name=cleaned,
            status=PENDING,
            visible_to_operators=False,
            created_by=created_by,
        )
        for role in normalized:
            org.roles.append(OrganizationRole(role=role))
        session.add(org)
        session.flush()

        return {
            "organization_id": org.id,
            "name": org.name,
            "roles": normalized,
            "status": org.status,
            "visible_to_operators": False,
            "duplicate": False,
        }


def approve_organization(database_url: str, organization_id: str) -> dict:
    factory = make_session_factory(database_url)
    with factory.begin() as session:
        org = session.get(Organization, organization_id)
        if org is None:
            raise ValueError("Organization not found.")
        org.status = APPROVED
        org.visible_to_operators = True
        org.approved_at = datetime.now(timezone.utc)
        return {
            "organization_id": org.id,
            "name": org.name,
            "status": org.status,
            "visible_to_operators": True,
        }


def add_supplier_source(
    database_url: str,
    *,
    organization_id: str,
    label: str,
    connector_key: str,
    source_type: str,
    base_url: str,
    capabilities: list[str],
    catalog_roots: list[dict],
    status: str = "READY",
    operator_browsable: bool = True,
) -> dict:
    factory = make_session_factory(database_url)
    with factory.begin() as session:
        org = session.get(Organization, organization_id)
        if org is None or org.status != APPROVED:
            raise ValueError("Approved Organization is required.")

        source = SupplierSource(
            id=new_id("src"),
            organization_id=organization_id,
            label=label.strip(),
            connector_key=connector_key.strip(),
            source_type=source_type.strip(),
            base_url=base_url.rstrip("/"),
            status=status,
            capabilities_json=json.dumps(sorted(set(capabilities)), ensure_ascii=False),
            catalog_roots_json=json.dumps(catalog_roots, ensure_ascii=False),
            operator_browsable=operator_browsable,
            read_only=True,
        )
        session.add(source)
        session.flush()
        return {
            "source_id": source.id,
            "organization_id": source.organization_id,
            "label": source.label,
            "connector_key": source.connector_key,
            "status": source.status,
            "operator_browsable": source.operator_browsable,
            "read_only": source.read_only,
        }


def list_operator_organizations(database_url: str) -> list[dict]:
    factory = make_session_factory(database_url)
    with factory() as session:
        rows = session.scalars(
            select(Organization)
            .where(
                Organization.status == APPROVED,
                Organization.visible_to_operators.is_(True),
            )
            .order_by(Organization.name)
        ).all()
        return [
            {
                "organization_id": org.id,
                "name": org.name,
                "roles": sorted(r.role for r in org.roles),
                "sources": [
                    {
                        "source_id": s.id,
                        "label": s.label,
                        "connector_key": s.connector_key,
                        "source_type": s.source_type,
                        "base_url": s.base_url,
                        "status": s.status,
                        "operator_browsable": s.operator_browsable,
                        "read_only": s.read_only,
                        "capabilities": json.loads(s.capabilities_json),
                        "catalog_roots": json.loads(s.catalog_roots_json),
                    }
                    for s in org.sources
                ],
            }
            for org in rows
        ]


def seed_reference_stenso(database_url: str) -> None:
    """Seed an approved reference Organization + read-only source.

    Catalog roots are Admin configuration, not operator URL input.
    This is safe data only; no HTTP request is made here.
    """
    factory = make_session_factory(database_url)
    with factory.begin() as session:
        existing = session.scalar(
            select(Organization).where(Organization.name == "STENSO")
        )
        if existing:
            return

        org = Organization(
            id="org-stenso",
            name="STENSO",
            status=APPROVED,
            visible_to_operators=True,
            created_by="SYSTEM_REFERENCE_SEED",
            approved_at=datetime.now(timezone.utc),
        )
        org.roles.append(OrganizationRole(role="SUPPLIER"))
        org.roles.append(OrganizationRole(role="MANUFACTURER"))

        source = SupplierSource(
            id="src-stenso-public",
            label="STENSO Public Catalogue",
            connector_key="stenso_public",
            source_type="PUBLIC_WEBSITE",
            base_url="https://stenso.net",
            status="READY",
            capabilities_json=json.dumps(
                ["IDENTITY","IMAGES","PRICE","AVAILABILITY","VARIANTS","CATALOGUES"],
                ensure_ascii=False,
            ),
            catalog_roots_json=json.dumps(
                [
                    {
                        "key": "diadora-work-shoes",
                        "label": "Работни обувки DIADORA",
                        "url": "https://stenso.net/211-rabotni-obuvki-diadora",
                    }
                ],
                ensure_ascii=False,
            ),
            operator_browsable=True,
            read_only=True,
        )
        org.sources.append(source)
        session.add(org)
