from pathlib import Path
import sys
from dataclasses import dataclass
ROOT=Path(__file__).resolve().parents[1];ADMIN=ROOT/'admin-platform'
if str(ADMIN) not in sys.path:sys.path.insert(0,str(ADMIN))
from app.services.v073_phase46.calenda_runtime_governance import *
@dataclass(frozen=True)
class H:
 supplier_reference:str;calenda_product_id:str;brand:str;variants:tuple;warnings:tuple=();hydration_pass:bool=True;images:tuple=()
def test_blue_rejected_brand_cleaned_shared_images_removed():
 h=H('blue','31940','FRUIT OF THE LOOM Допълнителна информация',({'value':'White','image_url':'https://x/a.jpg'},{'value':'Navy','image_url':'https://x/a.jpg'}));x=postprocess_calenda_hydrated(h);assert x.supplier_reference=='';assert x.brand=='FRUIT OF THE LOOM';assert all(not v['image_url'] for v in x.variants)
def test_id_separate_role():assert postprocess_calenda_hydrated(H('ID35','31940','B',())).supplier_reference==''
def test_numeric_punt_preserved():
 for ref in ('22160','21185','965','PUNT-52','PUNT-158'):assert postprocess_calenda_hydrated(H(ref,'1','B',())).supplier_reference==ref
def test_unique_images_preserved_no_mpn():
 h=H('22160','1','B',({'value':'White','image_url':'https://calenda.bg/a.jpg'},{'value':'Black','image_url':'https://calenda.bg/b.jpg'}));x=postprocess_calenda_hydrated(h);assert all(v['image_url'] for v in x.variants);assert governance_snapshot(h)['manufacturer_mpn']==''
