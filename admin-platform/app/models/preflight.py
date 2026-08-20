from __future__ import annotations
from datetime import datetime, timezone
from sqlalchemy import String,Integer,Boolean,DateTime,ForeignKey,Text
from sqlalchemy.orm import Mapped,mapped_column
from app.core.db import Base

def utcnow(): return datetime.now(timezone.utc)

class ChannelCommercePolicy(Base):
    __tablename__='channel_commerce_policies'
    channel_id:Mapped[int]=mapped_column(ForeignKey('channels.id',ondelete='CASCADE'),primary_key=True)
    country_code:Mapped[str]=mapped_column(String(8),default='')
    currency_code:Mapped[str]=mapped_column(String(8),default='')
    standard_vat_rate:Mapped[str]=mapped_column(String(20),default='')
    publish_price_includes_vat:Mapped[bool]=mapped_column(Boolean,default=True)
    active:Mapped[bool]=mapped_column(Boolean,default=True)
    updated_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,onupdate=utcnow)

class SupplierEvidence(Base):
    __tablename__='supplier_evidence'
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    import_job_item_id:Mapped[int]=mapped_column(ForeignKey('import_job_items.id',ondelete='CASCADE'),index=True)
    fetched_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    http_status:Mapped[int]=mapped_column(Integer,default=0)
    final_url:Mapped[str]=mapped_column(String(1000),default='')
    title:Mapped[str]=mapped_column(String(500),default='')
    supplier_reference:Mapped[str]=mapped_column(String(160),default='',index=True)
    model_code:Mapped[str]=mapped_column(String(160),default='')
    price_text:Mapped[str]=mapped_column(String(120),default='')
    price_value:Mapped[str]=mapped_column(String(60),default='')
    currency_hint:Mapped[str]=mapped_column(String(20),default='')
    availability_text:Mapped[str]=mapped_column(String(300),default='')
    image_urls_json:Mapped[str]=mapped_column(Text,default='[]')
    sizes_json:Mapped[str]=mapped_column(Text,default='[]')
    evidence_json:Mapped[str]=mapped_column(Text,default='{}')
    evidence_hash:Mapped[str]=mapped_column(String(64),default='',index=True)

class ImportPreflight(Base):
    __tablename__='import_preflights'
    id:Mapped[int]=mapped_column(Integer,primary_key=True)
    import_job_id:Mapped[int]=mapped_column(ForeignKey('import_jobs.id',ondelete='CASCADE'),index=True)
    created_at:Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    status:Mapped[str]=mapped_column(String(40),default='BLOCKED')
    identity_gate:Mapped[str]=mapped_column(String(40),default='NOT_RUN')
    presence_gate:Mapped[str]=mapped_column(String(40),default='NOT_RUN')
    language_gate:Mapped[str]=mapped_column(String(40),default='NOT_RUN')
    price_vat_gate:Mapped[str]=mapped_column(String(40),default='NOT_RUN')
    ready_targets_json:Mapped[str]=mapped_column(Text,default='[]')
    blocked_targets_json:Mapped[str]=mapped_column(Text,default='[]')
    findings_json:Mapped[str]=mapped_column(Text,default='[]')
    report_json:Mapped[str]=mapped_column(Text,default='{}')
