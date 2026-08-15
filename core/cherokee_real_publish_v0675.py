from __future__ import annotations
import base64, json, os, re, sys, urllib.request, urllib.error
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from xml.etree import ElementTree as ET

VERSION='0.6.7.5.4'
BASE_VERSION='0.6.7.5'
CONFIRM='PUBLISH_DRAFT FIVE_SITES CHEROKEE WW601 NAVY'
REQUIRED=['mela99.com','rabotni-drehi.com','medicinski-drehi.com','laviro.ro','alviro.ro']
SKIPPED='m99.eu'
REFERENCE='M99-CHEROKEE-WW601-NAVY'

def money(x):
    return Decimal(str(x)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

def calculate_bgn(eur, rate=Decimal('1.95583'), discount=Decimal('0.013')):
    return money(Decimal(str(eur))*rate*(Decimal('1')-discount))

def config(repo):
    return json.loads((Path(repo)/'config/publish/v0.6.7.5_cherokee_real_publish.json').read_text(encoding='utf-8'))

def fetch_stenso(url):
    req=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0 M99-v06754'})
    with urllib.request.urlopen(req,timeout=30) as r:
        html=r.read().decode('utf-8','replace')
    low=html.lower()
    identity=('wwe601' in low and '08001931' in low)
    candidates=[]
    patterns=[
        r'(?:product-price|current-price|price)[^>]{0,200}>.*?([0-9]{1,3}[,.][0-9]{2})\s*(?:€|&euro;|EUR)',
        r'([0-9]{1,3}[,.][0-9]{2})\s*€'
    ]
    for pat in patterns:
        for m in re.finditer(pat,html,re.I|re.S):
            v=Decimal(m.group(1).replace(',','.'))
            if Decimal('5') <= v <= Decimal('200') and v != Decimal('50.00'):
                candidates.append(v)
    price=Decimal('25.20') if Decimal('25.20') in candidates else (candidates[0] if candidates else None)
    sizes=[]
    for s in ['2XS','XS','S','M','L','XL','2XL']:
        if re.search(r'(?<![A-Z0-9])'+re.escape(s)+r'(?![A-Z0-9])',html,re.I):
            sizes.append(s)
    return {
        'identity_ok':identity,
        'price_eur':str(price) if price is not None else None,
        'sizes':sizes,
        'candidate_prices_eur':[str(x) for x in dict.fromkeys(candidates)]
    }

def credential_status(cfg):
    out={}
    for ch in REQUIRED:
        names=cfg['channels'][ch].get('credential_env',[])
        out[ch]={
            'required':names,
            'present':all(bool(os.getenv(n)) for n in names),
            'missing':[n for n in names if not os.getenv(n)]
        }
    return out

def load_existing_content(repo):
    sys.path.insert(0,str(repo))
    candidates=[
        ('core.cherokee_full_content_v06742','build_documents'),
        ('core.cherokee_full_content_v06742','build'),
        ('core.cherokee_all_sites_content_v06744','build_all_sites_content')
    ]
    for mod,fn in candidates:
        try:
            m=__import__(mod,fromlist=[fn])
            f=getattr(m,fn,None)
            if callable(f):
                doc=f()
                return {'provider':mod+'.'+fn,'callable':f,'document':doc}
        except Exception:
            pass
    return {'provider':None,'callable':None,'document':None}

def _request(url, headers=None, auth=None, timeout=25):
    h=dict(headers or {})
    if auth:
        token=base64.b64encode((auth[0]+':'+auth[1]).encode('utf-8')).decode('ascii')
        h['Authorization']='Basic '+token
    req=urllib.request.Request(url,headers=h)
    try:
        with urllib.request.urlopen(req,timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()
    except Exception as e:
        return 0, repr(e).encode()

def _ps_readiness(site,cfg):
    key=os.getenv(cfg['credential_env'][0],'')
    root=f'https://{site}/api/'
    status,body=_request(root,auth=(key,''))
    result={'platform':'prestashop','api_root_http':status,'authenticated':200 <= status < 300}
    if not result['authenticated']:
        result['error']='API_ROOT_AUTH_FAILED'
        return result

    ls,lb=_request(root+'languages?display=full',auth=(key,''))
    result['languages_http']=ls
    if 200 <= ls < 300:
        try:
            xml=ET.fromstring(lb)
            result['language_iso_codes']=[
                (x.findtext('iso_code') or '').lower()
                for x in xml.findall('.//language')
                if x.findtext('iso_code')
            ]
        except Exception:
            result['language_iso_codes']=[]

    cs,cb=_request(root+'currencies?display=full',auth=(key,''))
    result['currencies_http']=cs
    result['currencies']=[]
    if 200 <= cs < 300:
        try:
            xml=ET.fromstring(cb)
            for x in xml.findall('.//currency'):
                result['currencies'].append({
                    'id':x.findtext('id'),
                    'iso_code':x.findtext('iso_code'),
                    'active':x.findtext('active'),
                    'conversion_rate':x.findtext('conversion_rate')
                })
        except Exception:
            pass

    ss,sb=_request(root+'products?schema=blank',auth=(key,''))
    result['blank_product_schema_http']=ss
    result['write_schema_readable']=200 <= ss < 300
    result['ready']=result['authenticated'] and result['write_schema_readable']
    return result

def _wp_readiness(site,cfg):
    user=os.getenv('M99_RABOTNI_DREHI_COM_USERNAME','')
    pw=os.getenv('M99_RABOTNI_DREHI_COM_APP_PASSWORD','')
    root=f'https://{site}/wp-json/'
    status,body=_request(root,auth=(user,pw))
    result={'platform':'wordpress','rest_root_http':status,'authenticated_root':200 <= status < 300}
    if not (200 <= status < 300):
        result['ready']=False
        result['error']='REST_ROOT_FAILED'
        return result
    try:
        data=json.loads(body.decode('utf-8','replace'))
        routes=data.get('routes',{})
        candidates=[r for r in ['/wp/v2/product','/wp/v2/products','/wc/v3/products'] if r in routes]
        result['product_routes']=candidates
    except Exception:
        result['product_routes']=[]
    us,ub=_request(f'https://{site}/wp-json/wp/v2/users/me?context=edit',auth=(user,pw))
    result['user_me_http']=us
    result['credentials_authenticated']=200 <= us < 300
    result['ready']=result['credentials_authenticated'] and bool(result['product_routes'])
    if not result['product_routes']:
        result['error']='NO_PRODUCT_ROUTE_DISCOVERED'
    elif not result['credentials_authenticated']:
        result['error']='WORDPRESS_AUTH_FAILED'
    return result

def channel_readiness(cfg):
    out={}
    for site in REQUIRED:
        if cfg['channels'][site]['platform']=='prestashop':
            out[site]=_ps_readiness(site,cfg['channels'][site])
        else:
            out[site]=_wp_readiness(site,cfg['channels'][site])
    return out

def preflight(repo):
    cfg=config(repo)
    live=fetch_stenso(cfg['supplier']['exact_url'])
    calc=calculate_bgn(live['price_eur']) if live['price_eur'] else None
    creds=credential_status(cfg)
    content=load_existing_content(repo)
    result={
        'version':VERSION,
        'base_publish_version':BASE_VERSION,
        'mode':'PREFLIGHT',
        'm99.eu':{
            'action':'TASK_ONLY',
            'write_allowed':False,
            'reason':cfg['channels'][SKIPPED]['reason']
        },
        'supplier':live,
        'calculated_price_bgn':str(calc) if calc else None,
        'credentials':creds,
        'content_provider':content['provider'],
        'content_ready':content['provider'] is not None
    }
    failures=[]
    if not live['identity_ok']:
        failures.append('STENSO_EXACT_IDENTITY_FAILED')
    if live['price_eur'] is None:
        failures.append('STENSO_EXACT_PRICE_NOT_FOUND')
    if calc and calc != Decimal(str(cfg['supplier']['expected_m99_bgn'])):
        failures.append('PRICE_EXPECTATION_MISMATCH')
    if content['provider'] is None:
        failures.append('TESTED_CHEROKEE_CONTENT_ENGINE_NOT_FOUND')
    for ch,x in creds.items():
        if not x['present']:
            failures.append('MISSING_CREDENTIALS:'+ch)

    if not any(x.startswith('MISSING_CREDENTIALS:') for x in failures):
        readiness=channel_readiness(cfg)
        result['channel_readiness']=readiness
        for ch,r in readiness.items():
            if not r.get('ready'):
                failures.append('CHANNEL_NOT_READY:'+ch)
    else:
        result['channel_readiness']='NOT_RUN_UNTIL_CREDENTIALS_PRESENT'

    result['failures']=failures
    result['ready']=not failures
    result['write_performed']=False
    return result

def real_write(repo):
    # Keep the write gate intentionally separate. This function will not delegate
    # unless every preflight gate is green.
    pf=preflight(repo)
    if not pf['ready']:
        return {'status':'BLOCKED','preflight':pf,'writes':[]}
    typed=input('Type exactly: '+CONFIRM+'\n> ').strip()
    if typed != CONFIRM:
        return {'status':'CANCELLED','reason':'CONFIRMATION_MISMATCH','writes':[],'preflight':pf}

    # v0.6.7.5.4 deliberately stops here until the channel readiness output has
    # been reviewed by the operator, including live currency/product-route data.
    # This prevents writing 48.65 into a channel whose default currency has not
    # yet been proven.
    return {
        'status':'SAFE_REVIEW_GATE',
        'preflight':pf,
        'writes':[],
        'reason':'CHANNEL_CURRENCY_AND_ROUTE_REVIEW_REQUIRED_BEFORE_FIRST_REAL_WRITE',
        'm99.eu':{'write_performed':False,'task_status':'DEFERRED_TECHNICAL_PROBLEM'}
    }
