from __future__ import annotations
import json
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import ImportJob,ImportJobItem,Product,Channel,UserChannelAccess,User

def authorized_target_codes(db:Session,user:User)->set[str]:
    if user.is_superuser:
        return set(db.scalars(select(Channel.code).where(Channel.active.is_(True))))
    rows=db.execute(
        select(Channel.code).join(UserChannelAccess,UserChannelAccess.channel_id==Channel.id)
        .where(UserChannelAccess.user_id==user.id,UserChannelAccess.can_import_new.is_(True),Channel.active.is_(True))
    )
    return {r[0] for r in rows}

def detect_existing(db:Session,supplier_reference:str)->tuple[str,int|None]:
    if not supplier_reference:
        return "UNRESOLVED",None
    p=db.scalar(select(Product).where(Product.supplier_reference==supplier_reference))
    if p:return "EXISTING",p.id
    return "NEW",None

def new_job_code()->str:
    return "M99-IMPORT-"+datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S-%f")[:-3]

def create_draft_job(db:Session,*,user:User,supplier_id:int,source_type:str,source_url:str,items:list[dict],requested_targets:list[str])->ImportJob:
    auth=authorized_target_codes(db,user)
    requested={x for x in requested_targets if x}
    authorized=sorted(requested & auth)
    blocked=sorted(requested - auth)
    job=ImportJob(
        job_code=new_job_code(),
        created_by_user_id=user.id,
        source_supplier_id=supplier_id,
        source_type=source_type,
        source_payload=json.dumps({"source_url":source_url,"item_count":len(items)},ensure_ascii=False),
        requested_targets=json.dumps(sorted(requested),ensure_ascii=False),
        authorized_targets=json.dumps(authorized,ensure_ascii=False),
        ready_targets="[]",
        blocked_targets=json.dumps(blocked,ensure_ascii=False),
        status="DRAFT",
    )
    db.add(job);db.flush()
    for item in items:
        ref=(item.get("supplier_reference") or "").strip()
        status,matched=detect_existing(db,ref)
        db.add(ImportJobItem(
            import_job_id=job.id,
            source_url=item["url"],
            source_title=(item.get("title") or "")[:500],
            supplier_reference=ref,
            detection_status=status,
            matched_product_id=matched,
            selected=True,
        ))
    db.commit();db.refresh(job)
    return job
