from datetime import datetime, timezone
import json
from sqlalchemy import select
from app.persistence.v073_phase2.database import make_session_factory as p2
from app.persistence.v073_phase2.models import Organization, SupplierSource
from app.persistence.v073_phase4.database import make_session_factory as p4
from app.persistence.v073_phase4.models import OrganizationDecisionAudit, SupplierSourceConfigurationAudit, new_id

def list_organizations(database_url):
    f=p2(database_url)
    with f() as s:
        rows=s.scalars(select(Organization).order_by(Organization.name)).all()
        return [{"organization_id":r.id,"name":r.name,"status":r.status,"visible_to_operators":r.visible_to_operators,
                 "roles":sorted(x.role for x in r.roles),
                 "sources":[{"source_id":x.id,"label":x.label,"connector_key":x.connector_key,"source_type":x.source_type,
                             "base_url":x.base_url,"status":x.status,"operator_browsable":x.operator_browsable,"read_only":x.read_only}
                            for x in r.sources]} for r in rows]

def decide_organization(database_url, *, organization_id, action, actor, reason=None, merge_target_organization_id=None):
    if action not in {"APPROVE","REJECT","MERGE_WITH_EXISTING","ACTIVATE_ROLE"}: raise ValueError("Invalid action")
    f=p2(database_url)
    with f.begin() as s:
        org=s.get(Organization,organization_id)
        if not org: raise ValueError("Organization not found")
        if action=="APPROVE":
            org.status="APPROVED"; org.visible_to_operators=True; org.approved_at=datetime.now(timezone.utc)
        elif action=="REJECT":
            org.status="REJECTED"; org.visible_to_operators=False
        elif action=="MERGE_WITH_EXISTING":
            if not merge_target_organization_id or not s.get(Organization,merge_target_organization_id):
                raise ValueError("Valid merge target required")
            org.status="MERGED"; org.visible_to_operators=False
        else:
            org.status="APPROVED"; org.visible_to_operators=True
    af=p4(database_url)
    with af.begin() as s:
        s.add(OrganizationDecisionAudit(id=new_id("orgaudit"),organization_id=organization_id,action=action,
            actor=actor,reason=reason,merge_target_organization_id=merge_target_organization_id))
    return {"organization_id":organization_id,"action":action}

def configure_supplier_source(database_url, *, organization_id, source_id, actor, status=None, operator_browsable=None, read_only=True):
    if read_only is False: raise ValueError("Supplier Browser sources remain read-only")
    f=p2(database_url)
    with f.begin() as s:
        src=s.get(SupplierSource,source_id)
        if not src or src.organization_id!=organization_id: raise ValueError("SupplierSource not found")
        if status is not None: src.status=status
        if operator_browsable is not None: src.operator_browsable=operator_browsable
        src.read_only=True
        summary={"status":src.status,"operator_browsable":src.operator_browsable,"read_only":True,"connector_key":src.connector_key}
    af=p4(database_url)
    with af.begin() as s:
        s.add(SupplierSourceConfigurationAudit(id=new_id("sourceaudit"),organization_id=organization_id,source_id=source_id,
            actor=actor,action="CONFIGURE",config_summary_json=json.dumps(summary)))
    return {"organization_id":organization_id,"source_id":source_id,**summary}
