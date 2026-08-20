from datetime import datetime,timezone
from sqlalchemy import or_,select
from sqlalchemy.orm import Session
from app.models.entities import User
from app.core.security import verify_password

def authenticate(db:Session,login:str,password:str):
    stmt=select(User).where(or_(User.username==login.strip(),User.email==login.strip().lower()),User.active.is_(True))
    user=db.scalar(stmt)
    if not user or not verify_password(password,user.password_hash): return None
    user.last_login_at=datetime.now(timezone.utc)
    db.add(user);db.commit();db.refresh(user)
    return user

def permission_codes(user:User)->set[str]:
    if user.is_superuser:return {"*"}
    out=set()
    for role in user.roles:
        for perm in role.permissions: out.add(perm.code)
    return out

def has_permission(user:User,code:str)->bool:
    p=permission_codes(user)
    return "*" in p or code in p
