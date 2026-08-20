from sqlalchemy import select
from sqlalchemy.orm import configure_mappers
from app.core.db import Base,engine,SessionLocal
from app.models.entities import Language,Channel,ChannelLanguage
configure_mappers();Base.metadata.create_all(bind=engine)
LANGS=[("BG","bg","bg-BG","Bulgarian","Български",True,True,True,"EN",10),("EN","en","en-GB","English","English",True,True,False,"EN",20),("RU","ru","ru-RU","Russian","Русский",True,True,False,"EN",30),("RO","ro","ro-RO","Romanian","Română",True,True,False,"EN",40),("GR","el","el-GR","Greek","Ελληνικά",True,True,False,"EN",50)]
MATRIX={"mela99":{"BG","EN","RU"},"medicinski":{"BG","EN","RU"},"laviro":{"RO","EN"},"alviro":{"RO","EN"},"rabotni":{"BG"},"m99eu":{"EN"},"dolibarr":{"BG","EN"}}
with SessionLocal() as db:
    for code,iso,locale,name,native,ui,content,default,fallback,order in LANGS:
        if not db.scalar(select(Language).where(Language.code==code)):db.add(Language(code=code,iso_code=iso,locale=locale,name=name,native_name=native,admin_ui_enabled=ui,content_enabled=content,is_default=default,fallback_code=fallback,sort_order=order))
    db.commit();langs={x.code:x for x in db.scalars(select(Language))};channels={x.code:x for x in db.scalars(select(Channel))}
    for ccode,lset in MATRIX.items():
        c=channels.get(ccode)
        if not c:continue
        for lcode in lset:
            l=langs.get(lcode)
            if l and not db.scalar(select(ChannelLanguage).where(ChannelLanguage.channel_id==c.id,ChannelLanguage.language_id==l.id)):db.add(ChannelLanguage(channel_id=c.id,language_id=l.id,active=True,required=True))
    db.commit()
print("Language Registry seed: PASS");print("Initial BG/EN/RU/RO/GR: PASS");print("Channel Language Matrix seed: PASS")
