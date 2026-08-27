from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import Supplier, User, UserPreference
from app.services.i18n import ui_for
from app.services.supplier_browser import inspect_supplier_page, hydrate_stenso_product
from app.services.canonical_preview import prepare_canonical_preview

router = APIRouter(prefix="/supplier-browser")
templates = Jinja2Templates(directory="app/templates")

def _current_user(request: Request, db: Session):
    uid = request.session.get("user_id")
    return db.get(User, int(uid)) if uid else None

def _ctx(request: Request, db: Session, user: User, **kw):
    code = request.session.get("lang")
    if not code:
        pref = db.get(UserPreference, user.id)
        code = pref.admin_language_code if pref else "BG"
    return {
        "request": request,
        "user": user,
        "ui": ui_for(code),
        "current_lang": code,
        **kw,
    }

@router.get("/canonical-preview")
def canonical_preview_runtime(
    request: Request,
    supplier_id: int,
    supplier_url: str,
    target: str = "m99eu",
    db: Session = Depends(get_db),
):
    """READ/VERIFY ONLY canonical preview.
    This endpoint never performs website/channel writes.
    """
    user = _current_user(request, db)
    if not user:
        return RedirectResponse("/login", 303)

    supplier = db.get(Supplier, supplier_id)
    if not supplier or not supplier.active or not supplier.browser_enabled:
        raise HTTPException(400, "Supplier not available")

    try:
        if "stenso.net" in (supplier.base_url or "").lower():
            product = hydrate_stenso_product(
                supplier_url, supplier.base_url, use_cache=True
            )
        else:
            inspected = inspect_supplier_page(supplier_url, supplier.base_url)
            product = inspected["products"][0] if inspected.get("products") else {
                "url": supplier_url,
                "title": inspected.get("title") or "",
                "supplier_reference": "",
                "price_text": "",
                "availability_text": "UNKNOWN",
                "images": [],
                "description": "",
                "specifications": [],
                "variants": [],
            }
        preview = prepare_canonical_preview(product, target_code=target)
    except Exception as exc:
        raise HTTPException(409, f"Canonical preview failed: {exc}")

    return templates.TemplateResponse(
        "supplier_browser/canonical_preview.html",
        _ctx(request, db, user, supplier=supplier, supplier_product=product, preview=preview),
    )
