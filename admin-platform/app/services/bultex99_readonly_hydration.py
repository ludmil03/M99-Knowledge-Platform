from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from urllib.parse import urlparse
from integrations.bultex99_supplier.models import PublicProduct
from integrations.bultex99_supplier.public_parser import parse_public_product

BULTEX_HOSTS={"bultex99.com","www.bultex99.com"}

@dataclass(frozen=True)
class ReadOnlyHydrationResult:
    product:PublicProduct
    http_status:int
    source_url:str
    write_performed:bool=False

class BultexHydrationError(RuntimeError): pass

def validate_bultex_url(url:str)->str:
    value=str(url or "").strip()
    p=urlparse(value)
    if p.scheme!="https" or (p.hostname or "").lower() not in BULTEX_HOSTS:
        raise BultexHydrationError("BULTEX_URL_NOT_ALLOWED")
    return value

def hydrate_bultex99_product(url:str,*,get:Callable[[str],tuple[int,str,str]])->ReadOnlyHydrationResult:
    requested=validate_bultex_url(url)
    status,final_url,html=get(requested)
    final=validate_bultex_url(final_url)
    if status!=200: raise BultexHydrationError(f"BULTEX_HTTP_{status}")
    product=parse_public_product(html,final)
    return ReadOnlyHydrationResult(product,status,final,False)
