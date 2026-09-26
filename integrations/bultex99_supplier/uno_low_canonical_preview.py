from __future__ import annotations
from dataclasses import dataclass, asdict
from decimal import Decimal, ROUND_HALF_UP
LANGUAGES=("bg","en","ru","ro")
PRODUCT_REF="5161"; MODEL="11720E"; SUPPLIER_SKU_SIZE36="06100764.36"
SOURCE_GROSS_EUR=Decimal("58.90"); UNDERCUT_MIN=Decimal("0.010"); UNDERCUT_MAX=Decimal("0.017")
@dataclass(frozen=True)
class Evidence:
    field:str; value:str; authority:str; source:str
@dataclass(frozen=True)
class LocalizedContent:
    name:str; h1:str; short_description:str; meta_title:str; meta_description:str
@dataclass(frozen=True)
class CanonicalPreview:
    product_ref:str; model:str; identity_status:str; languages:tuple[str,...]
    evidence:tuple[Evidence,...]; content:dict[str,LocalizedContent]
    supplier_gross_eur:str; allowed_publish_gross_eur_min:str; allowed_publish_gross_eur_max:str
    write_performed:bool=False
    def as_dict(self): return asdict(self)
def _money(v): return str(v.quantize(Decimal("0.01"),rounding=ROUND_HALF_UP))
def allowed_price_range(gross=SOURCE_GROSS_EUR):
    return _money(gross*(1-UNDERCUT_MAX)),_money(gross*(1-UNDERCUT_MIN))
def evidence_record():
    return (
      Evidence("brand","Panda","MANUFACTURER","Panda manufacturer evidence"),
      Evidence("model","11720E","MANUFACTURER","Panda manufacturer evidence"),
      Evidence("protection_class","S3S FO LG SR ESD","MANUFACTURER","Panda manufacturer evidence"),
      Evidence("standard","EN ISO 20345:2022+A1:2024","MANUFACTURER","Panda manufacturer evidence"),
      Evidence("sizes","36-48","SUPPLIER","Bultex99 public product evidence"),
      Evidence("supplier_sku_size_36",SUPPLIER_SKU_SIZE36,"SUPPLIER","Bultex99 public product evidence"),
      Evidence("supplier_gross_eur",_money(SOURCE_GROSS_EUR),"SUPPLIER","Bultex99 public product evidence"),
      Evidence("toe_cap","Aluminium, 200 J","SUPPLIER","Bultex99 public product evidence"),
      Evidence("puncture_resistance","Multilayer polyester, 1100 N","SUPPLIER","Bultex99 public product evidence"),
      Evidence("upper","Water-resistant microfiber suede + TPU","SUPPLIER","Bultex99 public product evidence"),
      Evidence("outsole","TriDuraFlex","SUPPLIER","Bultex99 public product evidence"),
      Evidence("weight","570 g","MANUFACTURER","Panda manufacturer evidence"),
    )
def localized_content():
    return {
"bg":LocalizedContent("Работни обувки Panda UNO LOW 11720E S3S FO LG SR ESD","Panda UNO LOW 11720E – работни обувки S3S FO LG SR ESD","Ниски защитни работни обувки Panda UNO LOW 11720E за размери 36–48. Моделът е класифициран S3S FO LG SR ESD по EN ISO 20345:2022+A1:2024 и използва алуминиево бомбе 200 J, многослойна полиестерна защита срещу пробиване 1100 N и подметка TriDuraFlex.","Panda UNO LOW 11720E | S3S FO LG SR ESD","Panda UNO LOW 11720E: защитни работни обувки 36–48, S3S FO LG SR ESD, EN ISO 20345:2022+A1:2024, алуминиево бомбе и TriDuraFlex."),
"en":LocalizedContent("Panda UNO LOW 11720E S3S FO LG SR ESD Safety Shoes","Panda UNO LOW 11720E – S3S FO LG SR ESD Safety Shoes","Low-cut Panda UNO LOW 11720E safety shoes in sizes 36–48. The model is classified S3S FO LG SR ESD to EN ISO 20345:2022+A1:2024 and uses a 200 J aluminium toe cap, 1100 N multilayer polyester puncture protection and a TriDuraFlex outsole.","Panda UNO LOW 11720E | S3S FO LG SR ESD","Panda UNO LOW 11720E safety shoes, sizes 36–48, S3S FO LG SR ESD, EN ISO 20345:2022+A1:2024, aluminium toe cap and TriDuraFlex outsole."),
"ru":LocalizedContent("Защитная обувь Panda UNO LOW 11720E S3S FO LG SR ESD","Panda UNO LOW 11720E — защитная обувь S3S FO LG SR ESD","Низкая защитная обувь Panda UNO LOW 11720E в размерах 36–48. Модель имеет классификацию S3S FO LG SR ESD по EN ISO 20345:2022+A1:2024, алюминиевый подносок 200 Дж, многослойную полиэстеровую защиту от прокола 1100 Н и подошву TriDuraFlex.","Panda UNO LOW 11720E | S3S FO LG SR ESD","Panda UNO LOW 11720E: защитная обувь 36–48, S3S FO LG SR ESD, EN ISO 20345:2022+A1:2024, алюминиевый подносок и подошва TriDuraFlex."),
"ro":LocalizedContent("Pantofi de protecție Panda UNO LOW 11720E S3S FO LG SR ESD","Panda UNO LOW 11720E – pantofi de protecție S3S FO LG SR ESD","Pantofi de protecție Panda UNO LOW 11720E, model jos, în mărimile 36–48. Modelul este clasificat S3S FO LG SR ESD conform EN ISO 20345:2022+A1:2024 și folosește bombeu din aluminiu de 200 J, protecție antiperforație din poliester multistrat de 1100 N și talpă TriDuraFlex.","Panda UNO LOW 11720E | S3S FO LG SR ESD","Panda UNO LOW 11720E: pantofi de protecție 36–48, S3S FO LG SR ESD, EN ISO 20345:2022+A1:2024, bombeu din aluminiu și talpă TriDuraFlex.")
}
def build_preview(identity_status="NEW"):
    if identity_status not in {"NEW","EXISTING","AMBIGUOUS","UNRESOLVED"}: raise ValueError("invalid identity status")
    lo,hi=allowed_price_range()
    return CanonicalPreview(PRODUCT_REF,MODEL,identity_status,LANGUAGES,evidence_record(),localized_content(),_money(SOURCE_GROSS_EUR),lo,hi,False)
def quality_gate(p):
    blockers=[]
    if p.identity_status in {"AMBIGUOUS","UNRESOLVED"}: blockers.append("IDENTITY_BLOCK")
    if tuple(p.content.keys()) != LANGUAGES: blockers.append("LANGUAGE_BLOCK")
    required={"model","protection_class","standard","sizes","supplier_gross_eur"}
    if not required.issubset({e.field for e in p.evidence}): blockers.append("EVIDENCE_BLOCK")
    if p.write_performed: blockers.append("UNEXPECTED_WRITE")
    return {"pass":not blockers,"blockers":blockers,"write_performed":False,"next_gate":"CHANNEL_PREFLIGHT_AND_OPERATOR_WRITE_APPROVAL" if not blockers else "BLOCKED"}
