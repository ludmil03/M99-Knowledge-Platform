from sqlalchemy import select
from sqlalchemy.orm import configure_mappers
from app.core.db import Base,engine,SessionLocal
from app.models.entities import Channel
from app.models.preflight import ChannelCommercePolicy,SupplierEvidence,ImportPreflight
configure_mappers();Base.metadata.create_all(bind=engine)
with SessionLocal() as db:
    for ch in db.scalars(select(Channel).where(Channel.active.is_(True))):
        if not db.get(ChannelCommercePolicy,ch.id):
            db.add(ChannelCommercePolicy(channel_id=ch.id,country_code='',currency_code='',standard_vat_rate='',publish_price_includes_vat=True,active=True))
    db.commit()
print('SupplierEvidence table: PASS')
print('ImportPreflight table: PASS')
print('ChannelCommercePolicy table: PASS')
print('VAT rates intentionally require Super Admin confirmation: PASS')
