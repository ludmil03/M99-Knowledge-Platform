from app.routers.rev31_source_category_governance import router as rev31_source_category_governance_router
from pathlib import Path
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.core.config import settings
from app.core.db import Base,engine
from app.routers import auth,pages,admin,supplier_browser,preflight,commerce,canonical_preview_runtime

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


app.include_router(canonical_preview_runtime.router)
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

# M99 v0.7.3 Phase 3 - Product Presence
from app.routers import product_presence as m99_product_presence
app.include_router(m99_product_presence.router)

# M99 v0.7.3 Phase 4
from app.routers import superadmin_organizations as m99_superadmin_organizations
app.include_router(m99_superadmin_organizations.router)
from app.routers import identity_review as m99_identity_review
app.include_router(m99_identity_review.router)

# M99 v0.7.3 Phase 4.5 Revision 4 - Graphical Real Test Center
from app.routers.real_test_center import router as real_test_center_router
app.include_router(real_test_center_router)

# Revision 31 Phase 3 - additive governance GUI
app.include_router(rev31_source_category_governance_router)


# REV31_PHASE4_2_OPERATOR_SINGLE_PRODUCT_M99EU
from app.routers.operator_single_product_publish import router as operator_single_product_publish_router
app.include_router(operator_single_product_publish_router)


# REV31_PHASE4_3_UNIFIED_ADD_PRODUCTS
from app.routers.unified_add_products import router as unified_add_products_router
app.include_router(unified_add_products_router)


# REV31_PHASE4_3_R3_7_IMPORT_FLOW
from app.routers.r37_add_products_flow import router as r37_add_products_flow_router
app.include_router(r37_add_products_flow_router)

