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
