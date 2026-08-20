from sqlalchemy import select
from sqlalchemy.orm import configure_mappers
from app.core.db import Base,engine,SessionLocal
from app.models.entities import Permission,Role,Channel,Supplier
print("M99 DB BOOTSTRAP")
configure_mappers(); print("Mapper validation: PASS")
Base.metadata.create_all(bind=engine); print("Schema create_all: PASS")
PERMISSIONS=[("product.read","Преглед на продукти"),("product.create","Създаване на продукти"),("product.update","Редакция на продукти"),("product.activate","Публична активация"),("import.create_job","Създаване на Import Job"),("import.execute","Изпълнение на import"),("import.select_targets","Избор на target channels"),("supplier.browse","Supplier Browser"),("sync.view","Преглед на Daily Sync"),("sync.run_manual","Ръчно стартиране на sync"),("pricing.view","Преглед на pricing"),("pricing.approve","Одобрение на pricing"),("audit.read","Audit log"),("users.manage","Управление на потребители"),("roles.manage","Управление на роли"),("settings.manage","Системни настройки")]
CHANNELS=[("mela99","mela99.com","https://mela99.com","web"),("medicinski","medicinski-drehi.com","https://medicinski-drehi.com","web"),("laviro","laviro.ro","https://laviro.ro","web"),("alviro","alviro.ro","https://alviro.ro","web"),("rabotni","rabotni-drehi.com","https://rabotni-drehi.com","web"),("m99eu","m99.eu","https://m99.eu","web"),("dolibarr","Dolibarr","","erp")]
SUPPLIERS=[("stenso","Stenso","https://stenso.net"),("palltex","Palltex","")]
with SessionLocal() as db:
    for code,desc in PERMISSIONS:
        if not db.scalar(select(Permission).where(Permission.code==code)): db.add(Permission(code=code,description=desc))
    for code,name,url,typ in CHANNELS:
        if not db.scalar(select(Channel).where(Channel.code==code)): db.add(Channel(code=code,name=name,base_url=url,channel_type=typ))
    for code,name,url in SUPPLIERS:
        if not db.scalar(select(Supplier).where(Supplier.code==code)): db.add(Supplier(code=code,name=name,base_url=url))
    db.commit()
    sr=db.scalar(select(Role).where(Role.code=="M99_SUPER_ADMIN"))
    if not sr:
        sr=Role(code="M99_SUPER_ADMIN",name="M99 Super Admin",description="Пълен административен достъп"); db.add(sr); db.flush()
    sr.permissions=list(db.scalars(select(Permission)))
    mr=db.scalar(select(Role).where(Role.code=="CHANNEL_MANAGER"))
    if not mr:
        mr=Role(code="CHANNEL_MANAGER",name="Channel Manager",description="Управление на разрешени канали"); db.add(mr); db.flush()
    allowed={"product.read","product.create","product.update","import.create_job","import.execute","import.select_targets","supplier.browse","sync.view","pricing.view","audit.read"}
    mr.permissions=list(db.scalars(select(Permission).where(Permission.code.in_(allowed))))
    db.commit()
print("RBAC seed: PASS")
print("Channels seed: PASS")
print("Suppliers seed: PASS")
print("M99 database initialized.")
