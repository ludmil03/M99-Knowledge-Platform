from __future__ import annotations
import json
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.models.entities import ImportJob,ImportJobItem,Product,ProductPresence,Channel,ChannelLanguage,Language,Supplier
from app.models.preflight import ChannelCommercePolicy,SupplierEvidence,ImportPreflight
from app.services.supplier_evidence import read_exact_product,EvidenceReadError

def _loads(s):
    try:return json.loads(s or '[]')
    except Exception:return []

def run_preflight(db:Session,job:ImportJob)->ImportPreflight:
    items=list(db.scalars(select(ImportJobItem).where(ImportJobItem.import_job_id==job.id,ImportJobItem.selected.is_(True)).order_by(ImportJobItem.id)))
    supplier=db.get(Supplier,job.source_supplier_id) if job.source_supplier_id else None
    target_codes=_loads(job.authorized_targets)
    channels={c.code:c for c in db.scalars(select(Channel).where(Channel.code.in_(target_codes)))} if target_codes else {}
    findings=[];item_reports=[];identity_states=[];evidence_ok=True
    for item in items:
        try:
            ev=read_exact_product(item.source_url,supplier.base_url if supplier else '')
            row=SupplierEvidence(import_job_item_id=item.id,http_status=ev['http_status'],final_url=ev['final_url'],title=ev['title'],supplier_reference=ev['supplier_reference'],model_code=ev['model_code'],price_text=ev['price_text'],price_value=ev['price_value'],currency_hint=ev['currency_hint'],availability_text=ev['availability_text'],image_urls_json=json.dumps(ev['images'],ensure_ascii=False),sizes_json=json.dumps(ev['sizes'],ensure_ascii=False),evidence_json=json.dumps(ev,ensure_ascii=False),evidence_hash=ev['evidence_hash'])
            db.add(row)
            ref=ev['supplier_reference'] or item.supplier_reference
            if ref:
                matches=list(db.scalars(select(Product).where(Product.supplier_reference==ref)))
                if len(matches)==0:state='NEW';matched=None
                elif len(matches)==1:state='EXISTING';matched=matches[0].id
                else:state='AMBIGUOUS';matched=None
            else:state='UNRESOLVED';matched=None
            item.supplier_reference=ref or '' ;item.detection_status=state;item.matched_product_id=matched
            identity_states.append(state)
            item_reports.append({'item_id':item.id,'title':ev['title'],'supplier_reference':ref,'model_code':ev['model_code'],'identity':state,'matched_product_id':matched,'price_value':ev['price_value'],'currency_hint':ev['currency_hint'],'images':len(ev['images']),'sizes':ev['sizes'],'evidence_hash':ev['evidence_hash']})
        except EvidenceReadError as e:
            evidence_ok=False;identity_states.append('UNRESOLVED');findings.append(f'ITEM_{item.id}_EVIDENCE_READ_FAIL: {e}')
            item_reports.append({'item_id':item.id,'identity':'UNRESOLVED','error':str(e)})
    identity_gate='PASS' if evidence_ok and identity_states and all(x in {'NEW','EXISTING'} for x in identity_states) else 'BLOCKED'
    if any(x=='AMBIGUOUS' for x in identity_states):findings.append('AMBIGUOUS_IDENTITY_PRESENT')
    if any(x=='UNRESOLVED' for x in identity_states):findings.append('UNRESOLVED_IDENTITY_PRESENT')

    presence_report=[];presence_gate='PASS'
    for ir in item_reports:
        pid=ir.get('matched_product_id')
        for code,ch in channels.items():
            if pid:
                p=db.scalar(select(ProductPresence).where(ProductPresence.product_id==pid,ProductPresence.channel_id==ch.id))
                presence_report.append({'item_id':ir['item_id'],'target':code,'presence':p.presence_status if p else 'NOT_REGISTERED','channel_product_id':p.channel_product_id if p else ''})
            else:
                presence_report.append({'item_id':ir['item_id'],'target':code,'presence':'NEW_PRODUCT_NO_CANONICAL_PRESENCE'})

    language_report=[];language_gate='PASS'
    for code,ch in channels.items():
        rows=db.execute(select(Language.code,ChannelLanguage.required).join(ChannelLanguage,ChannelLanguage.language_id==Language.id).where(ChannelLanguage.channel_id==ch.id,ChannelLanguage.active.is_(True),Language.active.is_(True))).all()
        active=[r[0] for r in rows];required=[r[0] for r in rows if r[1]]
        ok=bool(required)
        if not ok:
            language_gate='BLOCKED';findings.append(f'{code}: LANGUAGE_MATRIX_NOT_CONFIGURED')
        language_report.append({'target':code,'active_languages':active,'required_languages':required,'configured':ok,'content_validation':'PENDING_GENERATION'})

    price_report=[];ready=[];blocked=[]
    for code,ch in channels.items():
        pol=db.get(ChannelCommercePolicy,ch.id)
        reasons=[]
        if not pol or not pol.active:reasons.append('COMMERCE_POLICY_MISSING')
        else:
            if not pol.standard_vat_rate.strip():reasons.append('STANDARD_VAT_RATE_MISSING')
            if not pol.currency_code.strip():reasons.append('CURRENCY_MISSING')
            if not pol.country_code.strip():reasons.append('COUNTRY_MISSING')
            if not pol.publish_price_includes_vat:reasons.append('PUBLISH_PRICE_MUST_INCLUDE_VAT')
        if any(not ir.get('price_value') for ir in item_reports):reasons.append('SUPPLIER_PRICE_NOT_RESOLVED')
        ok=not reasons
        (ready if ok else blocked).append(code)
        price_report.append({'target':code,'pass':ok,'reasons':reasons,'country':pol.country_code if pol else '', 'currency':pol.currency_code if pol else '', 'standard_vat_rate':pol.standard_vat_rate if pol else '', 'publish_price_includes_vat':pol.publish_price_includes_vat if pol else None})
        for r in reasons:findings.append(f'{code}: {r}')
    price_gate='PASS' if channels and not blocked else 'BLOCKED'
    all_pass=identity_gate=='PASS' and presence_gate=='PASS' and language_gate=='PASS' and price_gate=='PASS'
    status='PREFLIGHT_READY' if all_pass else ('VERIFIED' if evidence_ok and identity_gate=='PASS' else 'BLOCKED')
    report={'job_code':job.job_code,'items':item_reports,'presence':presence_report,'languages':language_report,'price_vat':price_report,'rule':'PUBLISHED PRICE MUST INCLUDE STANDARD VAT','website_write':False}
    pf=ImportPreflight(import_job_id=job.id,status=status,identity_gate=identity_gate,presence_gate=presence_gate,language_gate=language_gate,price_vat_gate=price_gate,ready_targets_json=json.dumps(ready,ensure_ascii=False),blocked_targets_json=json.dumps(blocked,ensure_ascii=False),findings_json=json.dumps(findings,ensure_ascii=False),report_json=json.dumps(report,ensure_ascii=False))
    db.add(pf)
    if status=='PREFLIGHT_READY':job.status='PREFLIGHT_READY';job.ready_targets=json.dumps(ready,ensure_ascii=False)
    elif status=='VERIFIED':job.status='VERIFIED'
    db.commit();db.refresh(pf)
    return pf
