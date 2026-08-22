from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.db import Base,engine
from app.routers import auth,pages,admin,supplier_browser,preflight,commerce

if not settings.session_secret or settings.session_secret=='CHANGE_ME_GENERATE_LOCALLY':
    raise RuntimeError('M99_SESSION_SECRET is not configured.')

Path('data').mkdir(exist_ok=True)
Base.metadata.create_all(bind=engine)
app=FastAPI(title=settings.app_name)
app.add_middleware(SessionMiddleware,secret_key=settings.session_secret,max_age=settings.session_max_age,same_site='lax',https_only=settings.session_https_only)
app.mount('/static',StaticFiles(directory='app/static'),name='static')
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(admin.router)
app.include_router(supplier_browser.router)
app.include_router(preflight.router)
app.include_router(commerce.router)

@app.get('/health')
def health():return {'status':'ok','app':settings.app_name,'env':settings.env,'version':'0.7.0.6'}

# M99 v0.7.2 Phase 3 - Admin UI -> m99.eu publisher
from app.routers import product_publish as m99_product_publish
app.include_router(m99_product_publish.router)

# M99 v0.7.3 - Operator Product Import Wizard Foundation
from app.routers import product_import_wizard as m99_product_import_wizard
app.include_router(m99_product_import_wizard.router)

# M99 v0.7.3 Phase 2 Revision 1 - Live Supplier Browser
from app.routers import live_supplier_browser as m99_live_supplier_browser
app.include_router(m99_live_supplier_browser.router)
