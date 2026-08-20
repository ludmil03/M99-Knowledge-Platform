from sqlalchemy.orm import configure_mappers
from app.core.db import Base,engine
from app.models.entities import ImportJobItem
configure_mappers()
Base.metadata.create_all(bind=engine)
print("ImportJobItem table bootstrap: PASS")
print("v0.7.0.5 schema extension: PASS")
