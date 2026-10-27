from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.stage3_final_unified_intake import build_stage3_final_review
from app.services.stage4_ui_authorization_bridge import build_publish_preview
from app.services.stage5_production_authorization import build_authorization
from app.services.stage5_final_ui_publish import execute_ui_publish, FinalPublishBlocked, ReadbackFailed
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config
from app.services.stage5_ui_live_preflight_bridge import build_live_preflight_view
from app.services.stage5_production_readiness import run_production_readiness
from integrations.m99eu_prestashop.config import load_m99eu_prestashop_config
from integrations.m99eu_prestashop.readonly_preflight_r2 import OneShotBasicGetTransport, run_preflight

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
    session = _session(request)
    username = str(session.get("username") or session.get("user") or "operator")
    user = {
        "username": username,
        "full_name": str(session.get("full_name") or username),
        "email": str(session.get("email") or ""),
        "is_superuser": bool(session.get("is_superuser") or False),
    }
    ui = {
        "dashboard": "Dashboard",
        "catalog": "Catalog",
        "products": "Products",
        "presence": "Presence",
        "suppliers": "Suppliers",
        "imports": "Imports",
        "system": "System",
        "users": "Users",
        "roles": "Roles",
        "languages": "Languages",
        "audit": "Audit",
        "logout": "Logout",
    }
    context = {
        "step": step,
        "draft": draft.as_dict(),
        "organizations": approved_organizations(),
        "selection_modes": selection_modes(),
        "targets": available_targets(),
        "title": "Добави продукти",
        "user": user,
        "ui": ui,
        "current_lang": str(session.get("current_lang") or "BG").upper(),
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
    first_n: str = Form(""),
):
    auth = _require_auth(request)
    if auth:
        return auth

    draft = _load_draft(request)
    products = [x.strip() for x in product_refs.splitlines() if x.strip()]
    categories = [x.strip() for x in category_refs.splitlines() if x.strip()]

    raw_first_n = first_n.strip()
    parsed_first_n = None
    if raw_first_n:
        try:
            parsed_first_n = int(raw_first_n)
        except ValueError:
            return _render(request, "selection", draft, error="first_n трябва да е цяло число.")

    try:
        validate_selection(selection_mode, products, categories, parsed_first_n)
    except ValueError as exc:
        return _render(request, "selection", draft, error=str(exc))

    draft.selection_mode = selection_mode
    draft.selected_product_refs = products
    draft.selected_category_refs = categories
    draft.first_n = parsed_first_n
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

    final_result, final_context = build_stage3_final_review(draft)
    publish_preview = build_publish_preview(draft, final_result)

    draft.current_state = "ready_for_preflight"
    _save_draft(request, draft)

    return _render(
        request,
        "ready",
        draft,
        review=build_review_summary(draft),
        stage3_final=final_result,
        multi_selection=final_context["multi_selection"],
        multi_review=final_context["multi_review"],
        selection_blockers=final_context["selection_blockers"],
        publish_enabled=False,
        write_performed=False,
        stage4_publish_preview=publish_preview,
        # M99_STAGE4_UI_AUTHORIZATION_BEGIN / END
        message="Stage 3 Unified Product Intake е активен в review-only режим. Няма publish/write.",
    )

# M99_STAGE5_LIVE_PREFLIGHT_ROUTE_BEGIN
@router.post("/m99eu-live-preflight", response_class=HTMLResponse)
def m99eu_live_preflight(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth
    draft = _load_draft(request)
    if "m99.eu" not in draft.ready_targets:
        return _render(request, "ready", draft, review=build_review_summary(draft), error="m99.eu is not in READY target scope.", publish_enabled=False, write_performed=False)
    try:
        cfg = load_m99eu_prestashop_config()
        result = run_preflight(cfg, OneShotBasicGetTransport(cfg.base_url, cfg.api_key, cfg.timeout_seconds))
        return _render(request, "ready", draft, review=build_review_summary(draft), stage5_live_preflight=build_live_preflight_view(result), publish_enabled=False, write_performed=False, message="m99.eu read-only preflight completed. Publish remains locked.")
    except Exception as exc:
        return _render(request, "ready", draft, review=build_review_summary(draft), error="m99.eu read-only preflight BLOCKED: "+type(exc).__name__, publish_enabled=False, write_performed=False)
# M99_STAGE5_LIVE_PREFLIGHT_ROUTE_END

# M99_STAGE5_PRODUCTION_READINESS_ROUTE_BEGIN
@router.post("/production-readiness", response_class=HTMLResponse)
def stage5_production_readiness(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth
    draft = _load_draft(request)
    if "m99.eu" not in draft.ready_targets:
        return _render(request, "ready", draft, review=build_review_summary(draft), error="m99.eu is not READY.")
    try:
        cfg=load_m99eu_prestashop_config()
        readiness=run_production_readiness(cfg)
        _session(request)["m99_stage5_production_readiness"]={
            "ready":readiness.ready,"language_map":readiness.language_map,
            "tax_rules_group_id":readiness.tax_rules_group_id,"vat_rate":readiness.vat_rate,
            "next_reference":readiness.next_reference,"blockers":list(readiness.blockers),
        }
        return _render(request,"ready",draft,review=build_review_summary(draft),
            stage5_production_readiness=readiness,publish_enabled=False,write_performed=False,
            message="Production readiness READ-ONLY completed. Publish remains fail-closed until exact product plan is server-built.")
    except Exception as exc:
        return _render(request,"ready",draft,review=build_review_summary(draft),
            error="PRODUCTION READINESS BLOCKED: "+type(exc).__name__,publish_enabled=False,write_performed=False)
# M99_STAGE5_PRODUCTION_READINESS_ROUTE_END

# M99_STAGE5_FINAL_UI_PUBLISH_BEGIN
@router.post("/publish", response_class=HTMLResponse)
async def stage5_publish(request: Request):
    auth = _require_auth(request)
    if auth:
        return auth
    draft = _load_draft(request)
    form = await request.form()
    if "m99.eu" not in draft.ready_targets:
        return _render(request, "ready", draft, review=build_review_summary(draft), error="m99.eu is not READY.")
    token = str(form.get("scope_token") or "")
    operation = str(form.get("operation") or "")
    reference = str(form.get("reference") or "")
    target = str(form.get("target") or "")
    confirmed = str(form.get("operator_confirmed") or "") == "YES"
    plan_raw = _session(request).get("m99_stage5_authorization_plan")
    if not isinstance(plan_raw, dict):
        return _render(request, "ready", draft, review=build_review_summary(draft), error="No valid server-side AuthorizationPlan.")
    try:
        plan = build_authorization(**plan_raw)
        result = execute_ui_publish(
            cfg=load_m99eu_prestashop_config(), plan=plan,
            submitted_token=token, submitted_operation=operation,
            submitted_reference=reference, submitted_target=target,
            operator_confirmed=confirmed,
        )
    except (ValueError, FinalPublishBlocked, ReadbackFailed) as exc:
        return _render(request, "ready", draft, review=build_review_summary(draft), error="PUBLISH BLOCKED: " + str(exc))
    return _render(request, "ready", draft, review=build_review_summary(draft), publish_result=result, message="Publish and mandatory readback completed.")
# M99_STAGE5_FINAL_UI_PUBLISH_END

