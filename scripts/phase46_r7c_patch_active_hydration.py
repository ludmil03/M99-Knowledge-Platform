from pathlib import Path
import hashlib
TARGET_REL="admin-platform/app/services/v073_phase45/unified_add_products.py"
EXPECTED_SHA="07ba88a869ab53282bb0a01f054101de48da007565d317cb9b388d68cb456ebe"
IMPORT_LINE="from app.services.v073_phase46.calenda_runtime_governance import postprocess_calenda_hydrated\n"
RETURN_ANCHOR="            return CalendaPublicConnector(source.base_url).get_product(product_url)"
RETURN_LINE="            return postprocess_calenda_hydrated(CalendaPublicConnector(source.base_url).get_product(product_url))"
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def patched_text(text):
    if IMPORT_LINE.strip() in text and RETURN_LINE in text:return text
    if RETURN_ANCHOR not in text:raise RuntimeError('Active Calenda hydrate return anchor not found; refusing guessed patch.')
    a='from app.services.v073_phase45.calenda_public_connector import ('
    if IMPORT_LINE.strip() not in text:
        i=text.find(a)
        if i<0:raise RuntimeError('Calenda connector import anchor not found.')
        text=text[:i]+IMPORT_LINE+text[i:]
    return text.replace(RETURN_ANCHOR,RETURN_LINE,1)
def apply(repo):
    p=Path(repo)/TARGET_REL
    if not p.is_file():raise RuntimeError('Active unified_add_products service missing.')
    if sha(p)!=EXPECTED_SHA:raise RuntimeError('Unexpected active unified_add_products SHA; refusing guessed patch.')
    out=patched_text(p.read_text(encoding='utf-8'));compile(out,str(p),'exec');p.write_text(out,encoding='utf-8',newline='\n')
