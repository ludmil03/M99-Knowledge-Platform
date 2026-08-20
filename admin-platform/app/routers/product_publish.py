from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.m99eu_publish_service import (
    build_live_dry_run,
    create_inactive_after_ui_confirmation,
    live_preflight,
    result_to_dict,
)


router = APIRouter(prefix="/products/publish", tags=["product-publish"])
TEMPLATE_DIR = Path(__file__).resolve().parents[1] / "templates"
templates = Jinja2Templates(directory=str(TEMPLATE_DIR))


def _is_authenticated(request: Request) -> bool:
    try:
        session = request.session
    except Exception:
        session = {}

    if isinstance(session, dict):
        for key in ("user_id", "username", "user", "authenticated", "is_authenticated"):
            if session.get(key):
                return True

    user = getattr(getattr(request, "state", object()), "user", None)
    if user:
        return True

    return False


def _login_redirect():
    return RedirectResponse(url="/login", status_code=303)


@router.get("/m99eu", response_class=HTMLResponse)
def m99eu_publish_page(request: Request):
    if not _is_authenticated(request):
        return _login_redirect()
    return templates.TemplateResponse(
        request=request,
        name="products/publish_m99eu.html",
        context={"mode": "start", "title": "Добави продукт в m99.eu", "channel": "m99.eu"},
    )


@router.post("/m99eu/preflight", response_class=HTMLResponse)
def m99eu_preflight(request: Request):
    if not _is_authenticated(request):
        return _login_redirect()
    try:
        result = live_preflight()
        error = None
    except Exception as exc:
        result = None
        error = str(exc)
    return templates.TemplateResponse(
        request=request,
        name="products/publish_m99eu.html",
        context={"mode": "preflight", "title": "Проверка на m99.eu", "channel": "m99.eu", "result": result, "error": error},
    )


@router.post("/m99eu/dry-run", response_class=HTMLResponse)
def m99eu_dry_run(request: Request):
    if not _is_authenticated(request):
        return _login_redirect()
    try:
        result = result_to_dict(build_live_dry_run())
        error = None
    except Exception as exc:
        result = None
        error = str(exc)
    return templates.TemplateResponse(
        request=request,
        name="products/publish_m99eu.html",
        context={"mode": "dry_run", "title": "DRY RUN — m99.eu", "channel": "m99.eu", "result": result, "error": error},
    )


@router.post("/m99eu/create-inactive", response_class=HTMLResponse)
def m99eu_create_inactive(
    request: Request,
    confirmation: str = Form(""),
    operator_approved: str = Form(""),
):
    if not _is_authenticated(request):
        return _login_redirect()

    if operator_approved != "yes" or confirmation.strip() != "CREATE_INACTIVE":
        return templates.TemplateResponse(
            request=request,
            name="products/publish_m99eu.html",
            context={
                "mode": "create_blocked",
                "title": "Създаването е блокирано",
                "channel": "m99.eu",
                "error": "Изискват се operator approval и точно потвърждение CREATE_INACTIVE.",
            },
            status_code=400,
        )

    try:
        result = result_to_dict(create_inactive_after_ui_confirmation())
        error = None
        status = 200 if result["success"] else 409
    except Exception as exc:
        result = None
        error = str(exc)
        status = 502

    return templates.TemplateResponse(
        request=request,
        name="products/publish_m99eu.html",
        context={"mode": "create_result", "title": "Резултат от m99.eu", "channel": "m99.eu", "result": result, "error": error},
        status_code=status,
    )
