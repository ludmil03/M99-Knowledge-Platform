from __future__ import annotations

import json

from sqlalchemy import select

from app.persistence.v073_phase2.database import make_session_factory
from app.persistence.v073_phase2.models import ImportJob, ImportJobTarget, Organization, SupplierSource, new_id


def create_import_job(
    database_url: str,
    *,
    created_by: str,
    source_organization_id: str,
    source_id: str,
    selection_mode: str,
    selected_products: list[str],
    selected_categories: list[str],
    observation_ids: list[str],
    target_scope: dict[str, list[str]],
) -> dict:
    factory = make_session_factory(database_url)
    with factory.begin() as session:
        org = session.get(Organization, source_organization_id)
        source = session.get(SupplierSource, source_id)

        if org is None or org.status != "APPROVED" or not org.visible_to_operators:
            raise ValueError("Approved operator-visible Organization is required.")
        if source is None or source.organization_id != org.id:
            raise ValueError("SupplierSource does not belong to selected Organization.")
        if source.status != "READY" or not source.read_only:
            raise ValueError("SupplierSource is not READY/read-only.")

        requested = list(dict.fromkeys(target_scope.get("requested_targets", [])))
        authorized = set(target_scope.get("authorized_targets", []))
        ready = set(target_scope.get("ready_targets", []))
        blocked = set(target_scope.get("blocked_targets", []))

        job = ImportJob(
            id=new_id("M99-IMPORT"),
            created_by=created_by,
            source_organization_id=org.id,
            source_id=source.id,
            selection_mode=selection_mode,
            selected_products_json=json.dumps(selected_products, ensure_ascii=False),
            selected_categories_json=json.dumps(selected_categories, ensure_ascii=False),
            observation_ids_json=json.dumps(observation_ids, ensure_ascii=False),
            product_count=len(selected_products),
            identity_status="PENDING",
            dry_run=True,
            requires_confirmation=True,
            status="DRAFT",
        )

        for key in requested:
            job.targets.append(
                ImportJobTarget(
                    target_key=key,
                    requested=True,
                    authorized=key in authorized,
                    ready=key in ready,
                    blocked_reason="NOT_AUTHORIZED_OR_NOT_READY" if key in blocked else None,
                    result_status="PENDING",
                )
            )

        session.add(job)
        session.flush()
        job_id = job.id

    return get_import_job(database_url, job_id)


def get_import_job(database_url: str, job_id: str) -> dict:
    factory = make_session_factory(database_url)
    with factory() as session:
        job = session.scalar(select(ImportJob).where(ImportJob.id == job_id))
        if job is None:
            raise ValueError("ImportJob not found.")

        return {
            "job_id": job.id,
            "created_by": job.created_by,
            "source_organization_id": job.source_organization_id,
            "source_id": job.source_id,
            "selection_mode": job.selection_mode,
            "selected_products": json.loads(job.selected_products_json),
            "selected_categories": json.loads(job.selected_categories_json),
            "observation_ids": json.loads(job.observation_ids_json),
            "product_count": job.product_count,
            "identity_status": job.identity_status,
            "status": job.status,
            "dry_run": job.dry_run,
            "requires_confirmation": job.requires_confirmation,
            "requested_targets": [t.target_key for t in job.targets if t.requested],
            "authorized_targets": [t.target_key for t in job.targets if t.authorized],
            "ready_targets": [t.target_key for t in job.targets if t.ready],
            "blocked_targets": [t.target_key for t in job.targets if t.blocked_reason],
        }
