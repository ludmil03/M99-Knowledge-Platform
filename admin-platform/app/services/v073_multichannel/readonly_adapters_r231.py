from __future__ import annotations
import os, json, base64, urllib.request, urllib.error, urllib.parse
from pathlib import Path
from .channel_registry import CHANNELS
REFERENCE='M99 100018'
KNOWN_M99EU_ID=2041
class ReadOnlyAdapterError(RuntimeError): pass

def _load_env(repo, admin):
    for env_file in (repo/'.env', admin/'.env', repo/'config'/'.env'):
        if not env_file.exists(): continue
        for line in env_file.read_text(encoding='utf-8',errors='ignore').splitlines():
            s=line.strip()
            if not s or s.startswith('#') or '=' not in s: continue
            k,v=s.split('=',1); os.environ.setdefault(k.strip(),v.strip().strip('"').strip("'"))

def _find_env(channel_id, platform):
    stem=channel_id.upper().replace('.','_').replace('-','_')
    short=channel_id.split('.')[0].upper().replace('-','_')
    names=list(os.environ)
    def find(groups):
        for pref in (stem,short):
            for name in names:
                u=name.upper()
                if pref in u and all(g in u for g in groups) and os.environ.get(name): return name
        return None
    if platform in ('prestashop','thirtybees'):
        return {'base':find(('URL',)) or find(('BASE',)), 'key':find(('KEY',))}
    if platform=='woocommerce':
        return {'base':find(('URL',)) or find(('BASE',)), 'key':find(('CONSUMER','KEY')) or find(('CK',)), 'secret':find(('CONSUMER','SECRET')) or find(('CS',))}
    return {'base':find(('URL',)) or find(('BASE',)), 'key':find(('KEY',))}

def _get_json(url, headers=None, user=None, password=''):
    req=urllib.request.Request(url, method='GET', headers=headers or {})
    if user is not None:
        token=base64.b64encode((user+':'+password).encode()).decode(); req.add_header('Authorization','Basic '+token)
    try:
        with urllib.request.urlopen(req,timeout=15) as resp:
            raw=resp.read(2000000)
            try: data=json.loads(raw.decode('utf-8','replace'))
            except Exception: data=None
            return {'ok':True,'status':resp.status,'json':data}
    except urllib.error.HTTPError as exc: return {'ok':False,'status':exc.code,'error':'HTTP_ERROR'}
    except Exception as exc: return {'ok':False,'status':None,'error':type(exc).__name__}

def _ps_lookup(base,key,reference):
    url=base.rstrip('/')+'/api/products?filter[reference]='+urllib.parse.quote(reference,safe='')+'&display=full&output_format=JSON'
    result=_get_json(url,user=key)
    if not result['ok']: return {'connectivity':result,'products':[]}
    data=result.get('json') or {}; products=data.get('products',[]) if isinstance(data,dict) else []
    if isinstance(products,dict): products=[products]
    out=[]
    for product in products:
        if isinstance(product,dict):
            out.append({k:product.get(k) for k in ('id','reference','active','visibility','id_category_default','id_tax_rules_group','price','cache_default_attribute')})
    return {'connectivity':{'ok':True,'status':result['status']},'products':out}

def _wc_lookup(base,key,secret,reference):
    url=base.rstrip('/')+'/wp-json/wc/v3/products?'+urllib.parse.urlencode({'sku':reference,'per_page':20})
    result=_get_json(url,user=key,password=secret)
    if not result['ok']: return {'connectivity':result,'products':[]}
    data=result.get('json') or []; data=data if isinstance(data,list) else []
    out=[]
    for product in data:
        if isinstance(product,dict): out.append({'id':product.get('id'),'sku':product.get('sku'),'status':product.get('status'),'catalog_visibility':product.get('catalog_visibility'),'type':product.get('type'),'price':product.get('price'),'variations_count':len(product.get('variations') or []),'images_count':len(product.get('images') or [])})
    return {'connectivity':{'ok':True,'status':result['status']},'products':out}

def _dolibarr_lookup(base,key,reference):
    filt="(t.ref:like:'"+reference+"')"
    url=base.rstrip('/')+'/api/index.php/products?limit=100&sqlfilters='+urllib.parse.quote(filt,safe='')
    result=_get_json(url,headers={'DOLAPIKEY':key,'Accept':'application/json'})
    if not result['ok']: return {'connectivity':result,'products':[]}
    data=result.get('json') or []; data=data if isinstance(data,list) else []
    out=[{'id':x.get('id'),'ref':x.get('ref'),'label':x.get('label'),'status':x.get('status'),'status_buy':x.get('status_buy'),'price':x.get('price'),'tva_tx':x.get('tva_tx')} for x in data if isinstance(x,dict) and str(x.get('ref','')).strip()==reference]
    return {'connectivity':{'ok':True,'status':result['status']},'products':out}

def run(repo,admin,reference=REFERENCE):
    _load_env(repo,admin); rows=[]
    for channel in CHANNELS:
        cid=channel['channel_id']; platform=channel['platform']; cfg=_find_env(cid,platform)
        row={'channel_id':cid,'platform':platform,'version':channel['version'],'reference':reference,'credential_names':cfg,'credentials_present':all(cfg.values()),'lookup':None,'decision':'BLOCKED','write_allowed':False,'blockers':[]}
        if not all(cfg.values()): row['blockers'].append('API_CONFIGURATION_NOT_DISCOVERED'); rows.append(row); continue
        if platform in ('prestashop','thirtybees'): lookup=_ps_lookup(os.environ[cfg['base']],os.environ[cfg['key']],reference)
        elif platform=='woocommerce': lookup=_wc_lookup(os.environ[cfg['base']],os.environ[cfg['key']],os.environ[cfg['secret']],reference)
        else: lookup=_dolibarr_lookup(os.environ[cfg['base']],os.environ[cfg['key']],reference)
        row['lookup']=lookup
        if not lookup['connectivity'].get('ok'): row['blockers'].append('READONLY_CONNECTIVITY_FAILED')
        else:
            n=len(lookup['products'])
            if n==0: row['decision']='CREATE_CANDIDATE'
            elif n==1: row['decision']='UPDATE_EXISTING'
            else: row['blockers'].append('DUPLICATE_REFERENCE')
            if cid=='m99.eu' and n==1 and str(lookup['products'][0].get('id'))!='2041': row['decision']='BLOCKED'; row['blockers'].append('M99EU_EXPECTED_PRODUCT_2041_MISMATCH')
        rows.append(row)
    return {'version':'R7.3.0 R2.3.1','mode':'REAL_READONLY_GET','reference':reference,'write_allowed':False,'http_methods':['GET'],'channels':rows}
