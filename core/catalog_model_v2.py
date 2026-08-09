from dataclasses import dataclass, field
from typing import Optional

@dataclass
class ProductGroup:
    m99_id:str
    name:str
    category:str
    lifecycle:str="active"

@dataclass
class Product:
    m99_id:str
    product_group_id:str
    brand:str
    model:str
    manufacturer:Optional[str]=None
    status:str="active"

@dataclass
class Variant:
    m99_id:str
    product_id:str
    size:Optional[str]=None
    color:Optional[str]=None
    ean:Optional[str]=None
    stock_managed:bool=True
    status:str="active"

@dataclass
class SupplierProduct:
    variant_id:str
    supplier_id:str
    supplier_sku:Optional[str]=None
    purchase_price:Optional[float]=None
    currency:Optional[str]=None
    lead_time_days:Optional[int]=None
    minimum_order_quantity:Optional[float]=None
    active:bool=True

@dataclass
class CommercialProductGraph:
    product_group:ProductGroup
    product:Product
    variants:list[Variant]=field(default_factory=list)
    supplier_products:list[SupplierProduct]=field(default_factory=list)

    def suppliers_for_variant(self,variant_id:str)->list[SupplierProduct]:
        return [x for x in self.supplier_products if x.variant_id==variant_id and x.active]
