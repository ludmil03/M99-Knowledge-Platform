from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.product_import_wizard import (
    ImportWizardDraft,
    approved_organizations,
    available_targets,
    build_review_summary,
    propose_organization,
    resolve_target_scope,
    selection_modes,
    validate_selection,
)


router = APIRouter(prefix="/operator/add-products", tags=["operator-product-import"])
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parents[1] / "templates"))


def _session(request: Request) -> dict:
    try:
        return request.session
    except Exception as exc:
        raise RuntimeError(
            "Admin session middleware is required for the operator wizard."
        ) from exc


def _is_authenticated(request: Request) -> bool:
    try:
        session = request.session
    except Exception:
        return False

    if isinstance(session, dict):
        for key in ("user_id", "username", "user", "authenticated", "is_authenticated"):
            if session.get(key):
                return True

    user = getattr(getattr(request, "state", object()), "user", None)
    return bool(user)


def _require_auth(request: Request):
    if not _is_authenticated(request):
        return RedirectResponse(url="/login", status_code=303)
    return None


def _load_draft(request: Request) -> ImportWizardDraft:
    raw = _session(request).get("m99_import_wizard", {})
    draft = ImportWizardDraft()
    for key, value in raw.items():
        if hasattr(draft, key):
            setattr(draft, key, value)
    return draft


def _save_draft(request: Request, draft: ImportWizardDraft) -> None:
    _session(request)["m99_import_wizard"] = draft.as_dict()


def _render(request: Request, step: str, draft: ImportWizardDraft, **extra):
    context = {
        "step": step,
        "draft": draft.as_dict(),
        "organizations": approved_organizations(),
        "selection_modes": selection_modes(),
        "targets": available_targets(),
        "title": "Добави продукти",
    }
    context.update(extra)
    return templates.TemplateResponse(
        request=request,
        name="product_import_wizard/wizard.html",
        context=context,
    )


@router.get("", response_class=HTMLResponse)
def start(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = ImportWizardDraft()
    _save_draft(request, draft)
    return _render(request, "source", draft)


@router.post("/source", response_class=HTMLResponse)
def choose_source(request: Request, organization_id: str = Form("")):
    auth = _require_auth(request)
    if auth:
        return auth

    organizations = {o.organization_id: o for o in approved_organizations()}
    org = organizations.get(organization_id)
    if org is None:
        return _render(
            request,
            "source",
            _load_draft(request),
            error="Избери одобрен доставчик/производител.",
        )

    draft = _load_draft(request)
    draft.source_organization_id = org.organization_id
    draft.source_name = org.name
    draft.current_state = "selection"
    _save_draft(request, draft)
    return _render(request, "selection", draft)


@router.post("/organization-proposal", response_class=HTMLResponse)
def organization_proposal(
    request: Request,
    organization_name: str = Form(""),
    supplier_role: str = Form(""),
    manufacturer_role: str = Form(""),
):
    auth = _require_auth(request)
    if auth:
        return auth

    roles = []
    if supplier_role == "yes":
        roles.append("SUPPLIER")
    if manufacturer_role == "yes":
        roles.append("MANUFACTURER")

    try:
        proposal = propose_organization(organization_name, roles)
        error = None
    except ValueError as exc:
        proposal = None
        error = str(exc)

    return _render(
        request,
        "source",
        _load_draft(request),
        proposal=proposal,
        error=error,
    )


@router.post("/selection", response_class=HTMLResponse)
def choose_selection(
    request: Request,
    selection_mode: str = Form(""),
    product_refs: str = Form(""),
    category_refs: str = Form(""),
    first_n: int | None = Form(None),
):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = _load_draft(request)
    products = [x.strip() for x in product_refs.splitlines() if x.strip()]
    categories = [x.strip() for x in category_refs.splitlines() if x.strip()]

    try:
        validate_selection(selection_mode, products, categories, first_n)
    except ValueError as exc:
        return _render(request, "selection", draft, error=str(exc))

    draft.selection_mode = selection_mode
    draft.selected_product_refs = products
    draft.selected_category_refs = categories
    draft.first_n = first_n
    draft.identity_summary = "Ще бъде проверено за NEW / EXISTING / AMBIGUOUS / UNRESOLVED"
    draft.current_state = "identity"
    _save_draft(request, draft)
    return _render(request, "identity", draft)


@router.post("/identity", response_class=HTMLResponse)
def identity_review(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = _load_draft(request)
    draft.identity_summary = "Identity/Duplicate Review е задължителен преди бъдещ write."
    draft.current_state = "targets"
    _save_draft(request, draft)
    return _render(request, "targets", draft)


@router.post("/targets", response_class=HTMLResponse)
async def choose_targets(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth

    form = await request.form()
    requested = form.getlist("targets")
    scope = resolve_target_scope(requested)

    draft = _load_draft(request)
    draft.requested_targets = scope["requested_targets"]
    draft.authorized_targets = scope["authorized_targets"]
    draft.ready_targets = scope["ready_targets"]
    draft.blocked_targets = scope["blocked_targets"]

    if not draft.requested_targets:
        return _render(request, "targets", draft, error="Избери поне един target.")

    draft.current_state = "review"
    _save_draft(request, draft)
    return _render(
        request,
        "review",
        draft,
        review=build_review_summary(draft),
    )


@router.post("/review", response_class=HTMLResponse)
def review(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = _load_draft(request)
    return _render(
        request,
        "review",
        draft,
        review=build_review_summary(draft),
    )


@router.post("/prepare-preflight", response_class=HTMLResponse)
def prepare_preflight(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = _load_draft(request)
    if not draft.ready_targets:
        return _render(
            request,
            "review",
            draft,
            review=build_review_summary(draft),
            error="Няма READY target. Не може да се продължи.",
        )

    draft.current_state = "ready_for_preflight"
    _save_draft(request, draft)

    return _render(
        request,
        "ready",
        draft,
        review=build_review_summary(draft),
        message=(
            "Wizard Foundation е готова. Следващата версия ще свърже "
            "Identity Resolver, Supplier Browser и live per-channel Preflight. "
            "В тази версия НЕ се прави write."
        ),
    )
