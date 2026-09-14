from __future__ import annotations
from pathlib import Path

from fastapi import APIRouter,Depends,Form,HTTPException,Request
from fastapi.responses import RedirectResponse
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models.entities import ImportJob,User,UserPreference
from app.services.i18n import ui_for
from app.services.v073_phase46.content_manufacturer_intelligence import (
    build_content_bundle,
    discover_manufacturer_product,
    draft_context,
    fetch_exact_manufacturer_evidence,
    persist_confirmed_enrichment,
)
from app.services.v073_phase46.durable_draft_enrichment import (
    load as load_durable_enrichment,
    find_confirmed_exact as find_cross_job_confirmed_enrichment,
)

router=APIRouter(prefix="/content-intelligence",tags=["Phase 4.6 R3 Content Intelligence"])
templates=Jinja2Templates(directory=str(Path(__file__).resolve().parents[1]/"templates"))

def _auth(request,db,job_id):
    uid=request.session.get("user_id")
    user=db.get(User,int(uid)) if uid else None
    if not user:
        return None,None
    job=db.get(ImportJob,int(job_id))
    if not job:
        raise HTTPException(404,"Import Job not found")
    if not user.is_superuser and job.created_by_user_id!=user.id:
        raise HTTPException(403,"Not authorized")
    return user,job

def _ctx(request,db,user,**kw):
    code=request.session.get("lang")
    if not code:
        pref=db.get(UserPreference,user.id)
        code=pref.admin_language_code if pref else "BG"
    return {"request":request,"user":user,"ui":ui_for(code),"current_lang":code,**kw}

def _review_context(c,*,request,db,user,job,target,source_uuid,product_url,discovery=None,
                    discovery_error="",content=None,manufacturer=None,saved=False,persistence_result=None,
                    publish_review_url="",durable_readback=None):
    return _ctx(
        request,db,user,
        job=job,target=target,source_uuid=source_uuid,product_url=product_url,
        supplier=c["supplier_evidence"],
        manufacturer=c["manufacturer_evidence"] if manufacturer is None else manufacturer,
        manufacturer_source=c.get("manufacturer_source") or {},
        manufacturer_product_code=c.get("manufacturer_product_code") or {},
        content=c["content_enrichment"] if content is None else content,
        discovery=discovery,
        discovery_error=discovery_error,
        saved=saved,
        persistence_result=persistence_result,
        supplier_context_source=c.get("supplier_context_source"),
        persistence=c.get("persistence"),
        publish_review_url=publish_review_url,
        durable_readback=durable_readback or {},
    )


def _verified_durable_readback(c:dict, *, job_id:int, target:str, product_url:str)->dict:
    """Resolve checksum-verified durable manufacturer/content evidence.

    Priority:
      1) exact sidecar for this job;
      2) newest exact cross-job match for the same supplier product.

    Cross-job matching is intentionally exact and fail-closed.
    """
    current_supplier=dict(c.get("supplier_evidence") or {})
    current_ref=str(current_supplier.get("supplier_reference") or "").strip()
    current_url=str(current_supplier.get("url") or product_url or "").strip().rstrip("/")
    if not current_ref:
        return {}

    stored=load_durable_enrichment(int(job_id))
    source_mode="SAME_JOB"
    if not stored:
        stored=find_cross_job_confirmed_enrichment(
            supplier_reference=current_ref,
            target=target,
            product_url=current_url,
        )
        source_mode="CROSS_JOB_EXACT"
    if not stored:
        return {}

    if str(stored.get("target") or "").strip()!=str(target or "").strip():
        raise RuntimeError("Durable readback target mismatch.")

    stored_ref=str(stored.get("supplier_reference") or "").strip()
    if stored_ref!=current_ref:
        raise RuntimeError("Durable readback supplier-reference mismatch.")

    stored_supplier=dict(stored.get("supplier_evidence") or {})
    stored_url=str(stored_supplier.get("url") or "").strip().rstrip("/")
    if current_url and stored_url and current_url!=stored_url:
        raise RuntimeError("Durable readback supplier-product URL mismatch.")

    manufacturer=dict(stored.get("manufacturer_evidence") or {})
    content=dict(stored.get("content_bundle") or {})
    if manufacturer.get("status") not in {"OPERATOR_CONFIRMED_EXACT","CONFIRMED_EXACT"}:
        raise RuntimeError("Durable manufacturer evidence is not in an accepted confirmed state.")
    if not content.get("documents"):
        raise RuntimeError("Durable content bundle is incomplete.")

    return {
        "verified":True,
        "source_mode":source_mode,
        "source_job_id":int(stored.get("job_id") or 0),
        "schema":stored.get("schema"),
        "payload_sha256":stored.get("payload_sha256"),
        "confirmed_at_utc":stored.get("confirmed_at_utc"),
        "manufacturer_evidence":manufacturer,
        "content_bundle":content,
        "supplier_reference":stored_ref,
        "target":stored.get("target"),
    }

@router.get("/review",response_class=HTMLResponse)
def review(request:Request,job_id:int,source_uuid:str,product_url:str,target:str="m99eu",saved:int=0,db:Session=Depends(get_db)):
    user,job=_auth(request,db,job_id)
    if not user:
        return RedirectResponse("/login",303)
    c=draft_context(db,job_id,source_uuid,product_url)
    manufacturer=c["manufacturer_evidence"]
    content=c["content_enrichment"]
    durable={}
    readback_error=""
    try:
        durable=_verified_durable_readback(
            c,job_id=job_id,target=target,product_url=product_url,
        )
    except Exception as exc:
        # Fail closed: a broken/mismatched durable sidecar is never silently trusted.
        readback_error=f"Durable manufacturer readback blocked safely: {exc}"

    if durable:
        manufacturer=durable["manufacturer_evidence"]
        # Durable evidence is authoritative, but customer-facing content is
        # derived with the current generator so accepted cross-job evidence
        # cannot keep stale semantic boilerplate or raw supplier HTML.
        content=build_content_bundle(
            supplier_evidence=c["supplier_evidence"],
            manufacturer_evidence=manufacturer,
            target_code=target,
        )
    elif manufacturer and not content:
        content=build_content_bundle(
            supplier_evidence=c["supplier_evidence"],
            manufacturer_evidence=manufacturer,
            target_code=target,
        )

    return templates.TemplateResponse(
        "content_intelligence/review.html",
        _review_context(
            c,request=request,db=db,user=user,job=job,target=target,
            source_uuid=source_uuid,product_url=product_url,
            manufacturer=manufacturer,content=content,
            saved=bool(saved or durable),
            persistence_result=(
                {"persisted":True,"reason":"DURABLE_READBACK_VERIFIED",
                 "payload_sha256":durable.get("payload_sha256")}
                if durable else None
            ),
            publish_review_url=(
                f"/content-intelligence/publish-handoff?job_id={int(job_id)}"
                if durable else ""
            ),
            durable_readback=durable,
            discovery_error=readback_error,
        ),
    )

@router.post("/discover",response_class=HTMLResponse)
def discover(
    request:Request,
    job_id:int=Form(...),
    source_uuid:str=Form(...),
    product_url:str=Form(...),
    target:str=Form("m99eu"),
    manufacturer_site_url:str=Form(""),
    db:Session=Depends(get_db),
):
    user,job=_auth(request,db,job_id)
    if not user:
        return RedirectResponse("/login",303)

    c=draft_context(db,job_id,source_uuid,product_url)
    s=c["supplier_evidence"]
    source=c.get("manufacturer_source") or {}
    code_info=c.get("manufacturer_product_code") or {}
    ref=str(code_info.get("code") or s.get("supplier_reference") or "").strip()
    title=str(s.get("name") or s.get("title") or "")

    # Default: use the already approved Manufacturer source automatically.
    # Manual URL remains only as an optional override.
    effective_site=(manufacturer_site_url or "").strip() or str(source.get("official_site") or "").strip()

    if not effective_site:
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                discovery_error=(
                    "Manufacturer is UNKNOWN or has no approved official site. "
                    "This does not block the DRAFT. You may leave Manufacturer empty "
                    "or provide a manual official-site override only if you know it."
                ),
            ),
        )

    try:
        d=discover_manufacturer_product(
            manufacturer_site_url=effective_site,
            supplier_reference=ref,
            title_hint=title,
        )
        provisional={}
        exact=d.get("exact_candidate")
        if exact:
            provisional=build_content_bundle(
                supplier_evidence=s,
                manufacturer_evidence={
                    "status":"UNCONFIRMED_EXACT_CANDIDATE",
                    "official_site":d["official_site"],
                    "official_product_url":exact["url"],
                    "manufacturer_product_code":ref,
                    "manufacturer_product_code_status":"EXACT_REFERENCE_CANDIDATE",
                    "page_title":exact["title"],
                    "meta_description":exact["meta_description"],
                    "images":exact["images"],
                    "documents":exact["documents"],
                    "tables":exact["tables"],
                    "text_excerpt":exact["text_excerpt"],
                },
                target_code=target,
            )
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                discovery=d,content=provisional,
            ),
        )
    except Exception as exc:
        # Never drop the operator into a raw 500 page for manufacturer discovery.
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                discovery_error=f"Manufacturer discovery failed safely: {exc}",
            ),
        )

@router.post("/confirm",response_class=HTMLResponse)
def confirm(
    request:Request,
    job_id:int=Form(...),
    source_uuid:str=Form(...),
    product_url:str=Form(...),
    target:str=Form("m99eu"),
    manufacturer_site_url:str=Form(...),
    manufacturer_page_url:str=Form(...),
    confirmation:str=Form(...),
    db:Session=Depends(get_db),
):
    user,job=_auth(request,db,job_id)
    if not user:
        return RedirectResponse("/login",303)
    if confirmation.strip()!="CONFIRM EXACT MANUFACTURER PRODUCT":
        raise HTTPException(409,"Exact manufacturer confirmation text is required.")

    c=draft_context(db,job_id,source_uuid,product_url)
    s=c["supplier_evidence"]
    code_info=c.get("manufacturer_product_code") or {}
    ref=str(code_info.get("code") or s.get("supplier_reference") or "").strip()
    title=str(s.get("name") or s.get("title") or "")

    try:
        evidence=fetch_exact_manufacturer_evidence(
            manufacturer_site_url=manufacturer_site_url,
            manufacturer_page_url=manufacturer_page_url,
            supplier_reference=ref,
            title_hint=title,
        )
        content=build_content_bundle(
            supplier_evidence=s,
            manufacturer_evidence=evidence,
            target_code=target,
        )
        persistence_result=persist_confirmed_enrichment(
            db,job_id=job_id,manufacturer_evidence=evidence,content_bundle=content,
            supplier_evidence=s,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                discovery_error=f"Manufacturer confirmation/content generation failed safely: {exc}",
            ),
        )

    try:
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                manufacturer=evidence,content=content,
                saved=bool(persistence_result.get("persisted")),
                persistence_result=persistence_result,
                publish_review_url=(f"/content-intelligence/publish-handoff?job_id={int(job_id)}" if persistence_result.get("persisted") else ""),
            ),
        )
    except Exception as exc:
        # Final UI boundary: a successful evidence/content/persistence operation
        # must never become a raw 500 solely because the review context/template fails.
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                manufacturer=evidence,content=content,
                saved=bool(persistence_result.get("persisted")),
                persistence_result=persistence_result,
                discovery_error=f"Confirmed data was produced, but the review UI failed safely: {exc}",
                publish_review_url="",
            ),
        )


@router.post("/confirm-palltex-bwolf-brand-owner", response_class=HTMLResponse)
def confirm_palltex_bwolf_brand_owner(
    request:Request,
    job_id:int=Form(...),
    source_uuid:str=Form(...),
    product_url:str=Form(...),
    target:str=Form("m99eu"),
    confirmation:str=Form(...),
    db:Session=Depends(get_db),
):
    """R7K.2 controlled exception: Palltex is both Supplier and Manufacturer/Brand owner for BWOLF.

    This is an explicit Super Admin assertion for this organization/brand relation only.
    It does NOT introduce a global Supplier == Manufacturer rule.
    The Palltex product page remains the exact official product evidence page.
    """
    user,job=_auth(request,db,job_id)
    if not user:
        return RedirectResponse("/login",303)
    if not user.is_superuser:
        raise HTTPException(403,"Palltex/BWOLF manufacturer resolution is Super Admin only.")
    exact="CONFIRM PALLTEX IS BWOLF MANUFACTURER"
    if confirmation.strip()!=exact:
        raise HTTPException(409,f"Exact confirmation required: {exact}")

    c=draft_context(db,job_id,source_uuid,product_url)
    s=dict(c["supplier_evidence"] or {})
    source_url=str(s.get("url") or product_url or "").strip()
    brand=str(s.get("brand") or s.get("manufacturer_name") or "").strip()
    supplier_ref=str(s.get("supplier_reference") or "").strip()
    from urllib.parse import urlparse
    p=urlparse(source_url)
    host=(p.hostname or "").lower().rstrip(".")
    if p.scheme.lower()!="https" or host not in {"palltex.bg","www.palltex.bg"} or "/p/" not in (p.path or ""):
        raise HTTPException(409,"R7K.2 applies only to an exact HTTPS Palltex product page.")
    if brand.casefold()!="bwolf":
        raise HTTPException(409,"R7K.2 applies only to verified supplier Brand evidence BWOLF.")
    if not supplier_ref:
        raise HTTPException(409,"Verified Palltex Supplier Reference is required.")

    # The same exact code is allowed to occupy two governed roles only because the
    # operator explicitly confirms Palltex as Manufacturer/Brand owner and the exact
    # official Palltex product page visibly carries that code. Roles remain separate.
    evidence={
        "status":"OPERATOR_CONFIRMED_EXACT",
        "resolution_mode":"PALLTEX_BWOLF_BRAND_OWNER_CONTROLLED",
        "manufacturer_name":"Палтекс",
        "brand_name":"BWOLF",
        "brand_owner":"Палтекс",
        "supplier_name":"Палтекс",
        "supplier_role":"SUPPLIER",
        "manufacturer_role":"MANUFACTURER_BRAND_OWNER",
        "roles_are_distinct":True,
        "official_site":"https://palltex.bg",
        "official_product_url":source_url,
        "manufacturer_product_code":supplier_ref,
        "manufacturer_product_code_status":"VERIFIED_EXACT_REFERENCE",
        "supplier_reference":supplier_ref,
        "supplier_reference_role":"SUPPLIER_MAPPING_ONLY",
        "manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY",
        "operator_assertion":exact,
        "operator_user_id":int(user.id),
        "evidence_basis":"EXACT_PALLTEX_PRODUCT_PAGE_PLUS_EXPLICIT_SUPER_ADMIN_BRAND_OWNER_ASSERTION",
        "images":list(s.get("images") or []),
        "documents":[],
        "tables":[],
        "page_title":str(s.get("name") or s.get("title") or ""),
        "meta_description":"",
        "text_excerpt":str(s.get("description") or "")[:4000],
    }
    try:
        content=build_content_bundle(
            supplier_evidence=s,
            manufacturer_evidence=evidence,
            target_code=target,
        )
        persistence_result=persist_confirmed_enrichment(
            db,job_id=job_id,manufacturer_evidence=evidence,
            content_bundle=content,supplier_evidence=s,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            "content_intelligence/review.html",
            _review_context(
                c,request=request,db=db,user=user,job=job,target=target,
                source_uuid=source_uuid,product_url=product_url,
                discovery_error=f"R7K.2 Palltex/BWOLF confirmation failed safely: {exc}",
            ),
        )

    return templates.TemplateResponse(
        "content_intelligence/review.html",
        _review_context(
            c,request=request,db=db,user=user,job=job,target=target,
            source_uuid=source_uuid,product_url=product_url,
            manufacturer=evidence,content=content,
            saved=bool(persistence_result.get("persisted")),
            persistence_result=persistence_result,
            publish_review_url=(f"/content-intelligence/publish-handoff?job_id={int(job_id)}" if persistence_result.get("persisted") else ""),
        ),
    )


@router.get("/publish-handoff", name="phase46_r4_publish_handoff")
def phase46_r4_publish_handoff(request: Request, job_id: int):
    """Resolve the already-active R1 FINAL review route from the real app graph.

    This intentionally avoids assuming the parent-router prefix. No channel write occurs.
    """
    candidates=[]
    for route in request.app.routes:
        path=getattr(route,"path","") or ""
        methods=set(getattr(route,"methods",set()) or set())
        if path.rstrip("/").endswith("/r1-final") and "GET" in methods:
            candidates.append(path.rstrip("/"))
    candidates=sorted(set(candidates), key=lambda x:(len(x),x))
    if not candidates:
        raise HTTPException(status_code=503, detail="R1 FINAL publish review route is not active in the current runtime route graph.")
    return RedirectResponse(url=f"{candidates[0]}?job_id={int(job_id)}", status_code=303)
