import json
from sqlalchemy.orm import Session
from app.models.entities import AuditLog

def log_event(db:Session,*,user_id=None,action="",entity_type="",entity_id="",result="OK",details=None,ip_address=""):
    row=AuditLog(user_id=user_id,action=action,entity_type=entity_type,entity_id=str(entity_id or ""),result=result,
                 details=json.dumps(details or {},ensure_ascii=False),ip_address=ip_address or "")
    db.add(row);db.commit()
