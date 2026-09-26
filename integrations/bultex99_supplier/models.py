from dataclasses import dataclass,field,asdict
from decimal import Decimal
from typing import Optional

@dataclass(frozen=True)
class PublicProduct:
    supplier_product_id:str
    source_url:str
    name:str
    supplier_sku:Optional[str]=None
    gross_price_eur:Optional[Decimal]=None
    availability:Optional[str]=None
    brand:Optional[str]=None
    standard:Optional[str]=None
    description:Optional[str]=None
    category_refs:tuple[str,...]=()
    legacy_stenso_refs:tuple[str,...]=()

@dataclass(frozen=True)
class IdentityPreview:
    supplier_product_id:str
    status:str
    evidence:tuple[str,...]=()

@dataclass
class DryRunItem:
    supplier_product_id:str
    source_url:str
    name:str
    identity_status:str
    qa_status:str
    qa_errors:list[str]=field(default_factory=list)

@dataclass
class DryRunReport:
    source:str
    selection_mode:str
    selected_count:int
    requested_targets:list[str]
    authorized_targets:list[str]
    ready_targets:list[str]
    blocked_targets:list[str]
    items:list[DryRunItem]
    write_performed:bool=False
    def as_dict(self): return asdict(self)
