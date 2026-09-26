from __future__ import annotations
from urllib.parse import urlparse
import re

def legacy_stenso_product_id(url:str)->str|None:
    if (urlparse(url).hostname or "").lower() not in {"stenso.net","www.stenso.net"}: return None
    m=re.search(r"/produkt/[^/]+/(\d+)-",urlparse(url).path)
    return m.group(1) if m else None

def migration_evidence(current_supplier_id:str,legacy_urls:list[str])->list[str]:
    # Evidence only: legacy IDs never become current canonical M99 IDs.
    return [u for u in legacy_urls if legacy_stenso_product_id(u)==str(current_supplier_id)]
