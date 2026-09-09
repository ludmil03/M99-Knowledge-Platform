from __future__ import annotations
from typing import Any
from app.services.v073_phase46.durable_draft_enrichment import load as load_enrichment
from app.services.v073_phase45.m99eu_r37_auto_publish import canonical_reference_from_draft
from app.services.v073_phase46.editorial_content_policy import policy_preview

REQUIRED_LANGUAGES=("EN","BG","RU")

def _spec(doc:dict,name_tokens:tuple[str,...])->str:
    for row in doc.get("technical_specifications") or []:
        name=str(row.get("name") or "").lower()
        if any(t.lower() in name for t in name_tokens):
            return str(row.get("value") or "").strip()
    return ""

def _variants(supplier:dict)->dict:
    variants=list(supplier.get("variants") or [])
    rows=[]; images=[]
    for v in variants:
        if not isinstance(v,dict):continue
        colour=str(v.get("value") or v.get("color") or "").strip()
        for key in ("image","image_url"):
            if v.get(key) and str(v[key]) not in images:images.append(str(v[key]))
        for im in v.get("images") or []:
            if str(im) not in images:images.append(str(im))
        for size in v.get("sizes") or []:
            if isinstance(size,dict):
                rows.append({"colour":colour,"size":str(size.get("size") or ""),"availability":str(size.get("availability") or size.get("status") or "")})
    return {"variant_groups":len(variants),"rows":rows,"images":images}

def build_canonical_payload_preview(*,job,item)->dict[str,Any]:
    blockers=[]; warnings=[]
    try: canonical=canonical_reference_from_draft(job=job,item=item)
    except Exception as exc:
        canonical=""; blockers.append("Canonical M99 reference: "+str(exc))

    durable=load_enrichment(int(job.id))
    if not durable:
        blockers.append("R4 durable enrichment is missing; reconfirm exact Manufacturer product.")
        return {"status":"BLOCKED","ready":False,"blockers":blockers,"warnings":warnings}

    if int(durable.get("job_id") or 0)!=int(job.id):blockers.append("Durable job_id mismatch.")
    if int(durable.get("item_id") or 0)!=int(item.id):blockers.append("Durable item_id mismatch.")
    if durable.get("target")!="m99eu":blockers.append("Durable target is not m99eu.")

    supplier=dict(durable.get("supplier_evidence") or {})
    manufacturer=dict(durable.get("manufacturer_evidence") or {})
    bundle=dict(durable.get("content_bundle") or {})
    docs=dict(bundle.get("documents") or {})
    supplier_ref=str(getattr(item,"supplier_reference","") or durable.get("supplier_reference") or "").strip()
    persisted_supplier_ref=str(durable.get("supplier_reference") or "").strip()
    if supplier_ref!=persisted_supplier_ref:blockers.append("Supplier reference mismatch between DRAFT and durable R4 evidence.")

    mref=""
    if manufacturer.get("status")=="OPERATOR_CONFIRMED_EXACT" and manufacturer.get("manufacturer_product_code_status")=="VERIFIED_EXACT_REFERENCE":
        mref=str(manufacturer.get("manufacturer_product_code") or "").strip()
    if not mref:blockers.append("Verified Manufacturer reference / MPN is missing.")
    if not manufacturer.get("official_product_url"):blockers.append("Exact official Manufacturer product URL is missing.")

    missing=[x for x in REQUIRED_LANGUAGES if x not in docs]
    if missing:blockers.append("Missing m99.eu language document(s): "+", ".join(missing))

    ident=dict(bundle.get("identifier_governance") or {})
    if ident.get("supplier_reference_role")!="SUPPLIER_MAPPING_ONLY":
        blockers.append("Content bundle predates supplier/manufacturer identifier governance; reconfirm Manufacturer to regenerate content.")
    if ident.get("manufacturer_reference_role")!="VERIFIED_MANUFACTURER_MPN_ONLY":
        blockers.append("Content bundle lacks verified Manufacturer/MPN role contract.")

    v=_variants(supplier)
    if not supplier:
        blockers.append("Supplier evidence is not durably persisted; reconfirm Manufacturer after bridge installation.")
    if not v["rows"]:blockers.append("Variant/availability evidence is missing from durable supplier evidence.")

    images=[]
    for im in list(manufacturer.get("images") or [])+list(supplier.get("images") or [])+v["images"]:
        im=str(im)
        if im and im not in images:images.append(im)
    if not images:blockers.append("No canonical product image evidence available.")

    language_preview={}
    for code in REQUIRED_LANGUAGES:
        d=docs.get(code) or {}
        language_preview[code]={
            "product_name":d.get("product_name") or "",
            "h1":d.get("h1") or "",
            "short_description":d.get("short_description") or "",
            "long_description_html":d.get("long_description_html") or "",
            "meta_title":d.get("meta_title") or "",
            "meta_description":d.get("meta_description") or "",
            "seo_keywords":d.get("seo_keywords") or [],
            "manufacturer_reference_in_specs":_spec(d,("manufacturer","производител","производителя","producător","κατασκευασ")),
        }
        if mref and language_preview[code]["manufacturer_reference_in_specs"]!=mref:
            blockers.append(f"{code}: Manufacturer reference / MPN is not explicitly represented in technical specifications.")

    if supplier_ref and mref and supplier_ref==mref:
        warnings.append("Supplier reference and Manufacturer MPN have the same value, but remain separate mappings/roles.")

    return {
        "schema":"m99.phase46.r4r1.canonical_payload_preview.v1",
        "status":"READY" if not blockers else "BLOCKED",
        "ready":not blockers,
        "write_allowed":False,
        "job_id":int(job.id),
        "item_id":int(item.id),
        "durable_sha256":durable.get("payload_sha256") or "",
        "identifiers":{
            "channel_reference":canonical,
            "channel_reference_role":"PERMANENT_M99_REFERENCE",
            "supplier_reference":supplier_ref,
            "supplier_reference_role":"SUPPLIER_MAPPING_ONLY",
            "manufacturer_reference":mref,
            "manufacturer_reference_role":"VERIFIED_MANUFACTURER_MPN_ONLY",
        },
        "manufacturer":{
            "official_site":manufacturer.get("official_site") or "",
            "official_product_url":manufacturer.get("official_product_url") or "",
            "evidence_status":manufacturer.get("status") or "",
        },
        "languages":language_preview,
        "images":{"count":len(images),"urls":images},
        "variants":{"groups":v["variant_groups"],"rows_count":len(v["rows"]),"rows":v["rows"]},
        "blockers":blockers,
        "editorial_policy":policy_preview(),
        "warnings":warnings,
    }
