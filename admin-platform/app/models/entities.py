from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String,Integer,Boolean,DateTime,ForeignKey,Text,UniqueConstraint
from sqlalchemy.orm import Mapped,mapped_column,relationship
from app.core.db import Base

def utcnow(): return datetime.now(timezone.utc)

class UserRole(Base):
    __tablename__="user_roles"
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    role_id:Mapped[int]=mapped_column(ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True)

class RolePermission(Base):
    __tablename__="role_permissions"
    role_id:Mapped[int]=mapped_column(ForeignKey("roles.id",ondelete="CASCADE"),primary_key=True)
    permission_id:Mapped[int]=mapped_column(ForeignKey("permissions.id",ondelete="CASCADE"),primary_key=True)

class User(Base):
    __tablename__="users"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    username:Mapped[str]=mapped_column(String(80),unique=True,index=True)
    email:Mapped[str]=mapped_column(String(255),unique=True,index=True)
    password_hash:Mapped[str]=mapped_column(String(500))
    full_name:Mapped[str]=mapped_column(String(160),default="")
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    is_superuser:Mapped[bool]=mapped_column(Boolean,default=False)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    last_login_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    roles:Mapped[list["Role"]]=relationship(secondary="user_roles",back_populates="users",lazy="selectin")

class Role(Base):
    __tablename__="roles"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    code:Mapped[str]=mapped_column(String(80),unique=True)
    name:Mapped[str]=mapped_column(String(160))
    description:Mapped[str]=mapped_column(Text,default="")
    users:Mapped[list[User]]=relationship(secondary="user_roles",back_populates="roles",lazy="selectin")
    permissions:Mapped[list["Permission"]]=relationship(secondary="role_permissions",back_populates="roles",lazy="selectin")

class Permission(Base):
    __tablename__="permissions"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    code:Mapped[str]=mapped_column(String(140),unique=True)
    description:Mapped[str]=mapped_column(String(255),default="")
    roles:Mapped[list[Role]]=relationship(secondary="role_permissions",back_populates="permissions",lazy="selectin")

class Channel(Base):
    __tablename__="channels"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    code:Mapped[str]=mapped_column(String(80),unique=True)
    name:Mapped[str]=mapped_column(String(160))
    base_url:Mapped[str]=mapped_column(String(255),default="")
    channel_type:Mapped[str]=mapped_column(String(40),default="web")
    active:Mapped[bool]=mapped_column(Boolean,default=True)

class Supplier(Base):
    __tablename__="suppliers"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    code:Mapped[str]=mapped_column(String(80),unique=True)
    name:Mapped[str]=mapped_column(String(160))
    base_url:Mapped[str]=mapped_column(String(255),default="")
    browser_enabled:Mapped[bool]=mapped_column(Boolean,default=True)
    active:Mapped[bool]=mapped_column(Boolean,default=True)

class Product(Base):
    __tablename__="products"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    m99_reference:Mapped[str]=mapped_column(String(40),unique=True,index=True)
    supplier_reference:Mapped[str]=mapped_column(String(120),default="",index=True)
    name:Mapped[str]=mapped_column(String(255))
    lifecycle:Mapped[str]=mapped_column(String(30),default="draft")
    supplier_id:Mapped[int|None]=mapped_column(ForeignKey("suppliers.id"),nullable=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,onupdate=utcnow)

class ProductPresence(Base):
    __tablename__="product_presence"
    __table_args__=(UniqueConstraint("product_id","channel_id",name="uq_product_channel"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    product_id:Mapped[int]=mapped_column(ForeignKey("products.id",ondelete="CASCADE"))
    channel_id:Mapped[int]=mapped_column(ForeignKey("channels.id",ondelete="CASCADE"))
    channel_product_id:Mapped[str]=mapped_column(String(120),default="")
    channel_url:Mapped[str]=mapped_column(String(500),default="")
    presence_status:Mapped[str]=mapped_column(String(60),default="UNKNOWN")
    stock_status:Mapped[str]=mapped_column(String(60),default="UNKNOWN")
    publication_status:Mapped[str]=mapped_column(String(60),default="UNKNOWN")
    currency:Mapped[str]=mapped_column(String(10),default="")
    gross_price:Mapped[str]=mapped_column(String(40),default="")
    last_verified_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    last_sync_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    verification_error:Mapped[str]=mapped_column(Text,default="")

class ImportJob(Base):
    __tablename__="import_jobs"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    job_code:Mapped[str]=mapped_column(String(80),unique=True,index=True)
    created_by_user_id:Mapped[int|None]=mapped_column(ForeignKey("users.id"),nullable=True)
    source_supplier_id:Mapped[int|None]=mapped_column(ForeignKey("suppliers.id"),nullable=True)
    source_type:Mapped[str]=mapped_column(String(40),default="product")
    source_payload:Mapped[str]=mapped_column(Text,default="{}")
    requested_targets:Mapped[str]=mapped_column(Text,default="[]")
    authorized_targets:Mapped[str]=mapped_column(Text,default="[]")
    ready_targets:Mapped[str]=mapped_column(Text,default="[]")
    blocked_targets:Mapped[str]=mapped_column(Text,default="[]")
    status:Mapped[str]=mapped_column(String(40),default="DRAFT")
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    started_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)
    finished_at:Mapped[datetime|None]=mapped_column(DateTime(timezone=True),nullable=True)

class ImportJobItem(Base):
    __tablename__="import_job_items"
    __table_args__=(UniqueConstraint("import_job_id","source_url",name="uq_import_job_item_url"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    import_job_id:Mapped[int]=mapped_column(ForeignKey("import_jobs.id",ondelete="CASCADE"),index=True)
    source_url:Mapped[str]=mapped_column(String(1000))
    source_title:Mapped[str]=mapped_column(String(500),default="")
    supplier_reference:Mapped[str]=mapped_column(String(160),default="",index=True)
    detection_status:Mapped[str]=mapped_column(String(40),default="UNRESOLVED")
    matched_product_id:Mapped[int|None]=mapped_column(ForeignKey("products.id"),nullable=True)
    selected:Mapped[bool]=mapped_column(Boolean,default=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)

class AuditLog(Base):
    __tablename__="audit_log"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,index=True)
    user_id:Mapped[int|None]=mapped_column(ForeignKey("users.id"),nullable=True)
    action:Mapped[str]=mapped_column(String(140),index=True)
    entity_type:Mapped[str]=mapped_column(String(80),default="")
    entity_id:Mapped[str]=mapped_column(String(120),default="")
    result:Mapped[str]=mapped_column(String(40),default="OK")
    details:Mapped[str]=mapped_column(Text,default="")
    ip_address:Mapped[str]=mapped_column(String(80),default="")

class Language(Base):
    __tablename__="languages"
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    code:Mapped[str]=mapped_column(String(12),unique=True,index=True)
    iso_code:Mapped[str]=mapped_column(String(12),default="")
    locale:Mapped[str]=mapped_column(String(20),default="")
    name:Mapped[str]=mapped_column(String(120))
    native_name:Mapped[str]=mapped_column(String(120))
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    admin_ui_enabled:Mapped[bool]=mapped_column(Boolean,default=True)
    content_enabled:Mapped[bool]=mapped_column(Boolean,default=True)
    is_default:Mapped[bool]=mapped_column(Boolean,default=False)
    fallback_code:Mapped[str]=mapped_column(String(12),default="EN")
    text_direction:Mapped[str]=mapped_column(String(5),default="ltr")
    sort_order:Mapped[int]=mapped_column(Integer,default=100)

class UserPreference(Base):
    __tablename__="user_preferences"
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"),primary_key=True)
    admin_language_code:Mapped[str]=mapped_column(String(12),default="BG")

class UserChannelAccess(Base):
    __tablename__="user_channel_access"
    __table_args__=(UniqueConstraint("user_id","channel_id",name="uq_user_channel_access"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    user_id:Mapped[int]=mapped_column(ForeignKey("users.id",ondelete="CASCADE"))
    channel_id:Mapped[int]=mapped_column(ForeignKey("channels.id",ondelete="CASCADE"))
    can_read:Mapped[bool]=mapped_column(Boolean,default=True)
    can_import_new:Mapped[bool]=mapped_column(Boolean,default=False)
    can_update_existing:Mapped[bool]=mapped_column(Boolean,default=False)
    can_activate:Mapped[bool]=mapped_column(Boolean,default=False)
    can_run_sync:Mapped[bool]=mapped_column(Boolean,default=False)

class ChannelLanguage(Base):
    __tablename__="channel_languages"
    __table_args__=(UniqueConstraint("channel_id","language_id",name="uq_channel_language"),)
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    channel_id:Mapped[int]=mapped_column(ForeignKey("channels.id",ondelete="CASCADE"))
    language_id:Mapped[int]=mapped_column(ForeignKey("languages.id",ondelete="CASCADE"))
    required:Mapped[bool]=mapped_column(Boolean,default=True)
    active:Mapped[bool]=mapped_column(Boolean,default=True)
