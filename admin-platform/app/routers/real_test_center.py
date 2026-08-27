from pathlib import Path
from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.v073_phase45.real_test_center import (
    dashboard, run_local_persistence, run_stenso, run_m99eu_test,
    run_dolibarr_test, operator_decide
)

router = APIRouter(prefix="/operator/real-tests", tags=["real-tests"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))

def auth(r: Request):
    try:
        return bool(r.session.get("user_id") or r.session.get("username"))
    except Exception:
        return False

def actor(r: Request):
    try:
        return str(r.session.get("username") or r.session.get("user_id") or "operator")
    except Exception:
        return "operator"

def page(request: Request, message="", results=None, error=""):
    ctx = dashboard()
    ctx.update({
        "title": "Реални тестове",
        "message": message,
        "results": results or [],
        "error": error,
    })
    return templates.TemplateResponse(
        request=request,
        name="real_tests/index.html",
        context=ctx,
    )

@router.get("", response_class=HTMLResponse)
def home(request: Request):
    if not auth(request):
        return RedirectResponse("/login", 303)
    return page(request)

@router.post("/persistence", response_class=HTMLResponse)
def persistence(request: Request):
    if not auth(request):
        return RedirectResponse("/login", 303)
    try:
        return page(request, "Persistence тестът приключи.", run_local_persistence())
    except Exception as exc:
        return page(request, error=str(exc))

@router.post("/stenso", response_class=HTMLResponse)
def stenso(request: Request):
    if not auth(request):
        return RedirectResponse("/login", 303)
    try:
        return page(request, "STENSO live тестът приключи.", run_stenso())
    except Exception as exc:
        return page(request, error=str(exc))

@router.post("/m99eu", response_class=HTMLResponse)
def m99eu(
    request: Request,
    api_key: str = Form(...),
    base_url: str = Form("https://m99.eu"),
    category_id: str = Form("26"),
):
    if not auth(request):
        return RedirectResponse("/login", 303)
    try:
        results = run_m99eu_test(api_key, base_url, category_id)
        return page(
            request,
            "m99.eu тестът приключи. Успешният продукт НЕ се изтрива и чака операторска проверка.",
            results,
        )
    except Exception as exc:
        return page(request, error=str(exc))

@router.post("/dolibarr", response_class=HTMLResponse)
def dolibarr(
    request: Request,
    api_key: str = Form(...),
    base_url: str = Form(...),
):
    if not auth(request):
        return RedirectResponse("/login", 303)
    try:
        return page(request, "Dolibarr TEST CRUD приключи.", run_dolibarr_test(api_key, base_url))
    except Exception as exc:
        return page(request, error=str(exc))

@router.post("/operator-decision", response_class=HTMLResponse)
def decision(
    request: Request,
    decision: str = Form(...),
    notes: str = Form(""),
):
    if not auth(request):
        return RedirectResponse("/login", 303)
    try:
        data = operator_decide(decision, notes, actor(request))
        message = (
            "Продуктът е APPROVED и остава. Готов е за Daily Sync baseline."
            if data["operator_status"] == "APPROVED"
            else "Продуктът е REJECTED. Остава за FIX/RETEST или отделно операторско DELETE."
        )
        return page(request, message)
    except Exception as exc:
        return page(request, error=str(exc))
