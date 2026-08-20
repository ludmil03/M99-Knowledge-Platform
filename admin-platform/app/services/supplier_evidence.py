from __future__ import annotations
import hashlib,json,re
from urllib.parse import urljoin,urlparse
import httpx
from bs4 import BeautifulSoup

UA='M99KnowledgePlatform/0.7.0.6 (+exact supplier evidence; read only)'

class EvidenceReadError(RuntimeError): pass

def _decimal(raw:str)->str:
    if not raw:return ''
    s=raw.replace('\xa0',' ').strip()
    m=re.search(r'([0-9]{1,7}(?:[\s.,][0-9]{3})*(?:[.,][0-9]{1,2})?)',s)
    if not m:return ''
    v=m.group(1).replace(' ','')
    if ',' in v and '.' not in v:v=v.replace(',','.')
    elif ',' in v and '.' in v:
        if v.rfind(',')>v.rfind('.'):v=v.replace('.','').replace(',','.')
        else:v=v.replace(',','')
    return v

def _ref(text:str)->str:
    for p in [r'(?:Код|Референтен\s*номер|Артикул(?:ен)?\s*номер|Reference|Ref\.?)\s*[:#]?\s*([0-9A-Za-z._/-]{4,40})',r'\b(0[0-9]{7})\b']:
        m=re.search(p,text,re.I)
        if m:return m.group(1).strip()
    return ''

def _model(text:str)->str:
    candidates=re.findall(r'\b[A-Z]{2,8}[0-9]{2,6}[A-Z0-9-]{0,8}\b',text)
    for c in candidates:
        if not re.fullmatch(r'0[0-9]{7}',c):return c
    return ''

def read_exact_product(url:str,supplier_base_url:str='')->dict:
    try:
        with httpx.Client(follow_redirects=True,timeout=25,headers={'User-Agent':UA}) as c:
            r=c.get(url)
            if r.status_code>=400:raise EvidenceReadError(f'HTTP {r.status_code}')
    except httpx.HTTPError as e:raise EvidenceReadError(str(e)) from e
    final=str(r.url)
    if supplier_base_url and urlparse(final).netloc.lower()!=urlparse(supplier_base_url).netloc.lower():
        raise EvidenceReadError('Final URL host differs from configured supplier host')
    soup=BeautifulSoup(r.text,'html.parser')
    h1=soup.find('h1');title=(h1.get_text(' ',strip=True) if h1 else (soup.title.get_text(' ',strip=True) if soup.title else ''))[:500]
    text=soup.get_text(' ',strip=True)
    ref=_ref(text);model=_model(title+' '+text[:3000])
    price_text='';price_value='';currency=''
    for sel in ['[itemprop="price"]','meta[property="product:price:amount"]','meta[itemprop="price"]','.current-price','.price','span.price']:
        el=soup.select_one(sel)
        if not el:continue
        raw=(el.get('content') or el.get_text(' ',strip=True) or '').strip()
        val=_decimal(raw)
        if val:
            price_text=raw[:120];price_value=val
            break
    cmeta=soup.select_one('meta[property="product:price:currency"],meta[itemprop="priceCurrency"],[itemprop="priceCurrency"]')
    if cmeta:currency=(cmeta.get('content') or cmeta.get_text(' ',strip=True) or '')[:20]
    if not currency:
        if 'лв' in text or 'BGN' in text:currency='BGN'
        elif 'lei' in text.lower() or 'RON' in text:currency='RON'
        elif '€' in text or 'EUR' in text:currency='EUR'
    images=[]
    for img in soup.find_all('img'):
        src=img.get('data-src') or img.get('src')
        if not src:continue
        u=urljoin(final,src)
        if u.startswith(('http://','https://')) and u not in images:images.append(u)
        if len(images)>=20:break
    sizes=[]
    for el in soup.select('select option, .attribute_list label, .product-variants-item label, [data-product-attribute] option'):
        s=el.get_text(' ',strip=True)
        if s and len(s)<=30 and s.upper() not in {'ИЗБЕРИ','CHOOSE','SELECT'} and s not in sizes:sizes.append(s)
        if len(sizes)>=40:break
    availability=''
    for sel in ['[itemprop="availability"]','.product-availability','#product-availability','.availability']:
        el=soup.select_one(sel)
        if el:
            availability=(el.get('content') or el.get_text(' ',strip=True) or '')[:300];break
    evidence={'final_url':final,'http_status':r.status_code,'title':title,'supplier_reference':ref,'model_code':model,'price_text':price_text,'price_value':price_value,'currency_hint':currency,'availability_text':availability,'images':images,'sizes':sizes}
    canonical=json.dumps(evidence,sort_keys=True,ensure_ascii=False,separators=(',',':'))
    evidence['evidence_hash']=hashlib.sha256(canonical.encode('utf-8')).hexdigest()
    return evidence
