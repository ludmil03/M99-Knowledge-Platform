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
                    publish_review_url=""):
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
    )

@router.get("/review",response_class=HTMLResponse)
def review(request:Request,job_id:int,source_uuid:str,product_url:str,target:str="m99eu",saved:int=0,db:Session=Depends(get_db)):
    user,job=_auth(request,db,job_id)
    if not user:
        return RedirectResponse("/login",303)
    c=draft_context(db,job_id,source_uuid,product_url)
    manufacturer=c["manufacturer_evidence"]
    content=c["content_enrichment"]
    if manufacturer and not content:
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
            content=content,saved=bool(saved),
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
