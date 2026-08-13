from __future__ import annotations
from copy import deepcopy
from difflib import SequenceMatcher
import hashlib, json, re

VERSION="0.6.7.4.3"

IDENTITY={
 "brand":"Cherokee","collection":"WW Revolution","style":"WW601",
 "supplier_alias":"WWE601","manufacturer_item":"CK-WW601--","colour":"Navy"
}

CHANNELS={
 "mela99.com":{"languages":["bg","en","ru"],"intent":"commercial_product","platform":"prestashop_family","publication":"WRITE_DRAFT"},
 "m99.eu":{"languages":["bg","en","ru"],"intent":"technical_brand_catalogue","platform":"wordpress","publication":"WRITE_DRAFT"},
 "rabotni-drehi.com":{"languages":["bg","en","ru"],"intent":"professional_workwear_search","platform":"wordpress","publication":"WRITE_DRAFT"},
 "medicinski-drehi.com":{"languages":["bg","en","ru"],"intent":"medical_professional","platform":"adapter_required","publication":"WRITE_DRAFT"},
 "laviro.ro":{"languages":["ro","en"],"intent":"romanian_medical_commercial","platform":"prestashop_family","publication":"WRITE_DRAFT"},
 "alviro.ro":{"languages":["ro","en"],"intent":"romanian_professional_catalogue","platform":"adapter_required","publication":"WRITE_DRAFT"}
}

FACTS={
 "material_raw":"78% polyester, 20% rayon, 2% spandex",
 "material_bg":"78% полиестер, 20% вискоза, 2% еластан",
 "material_ru":"78% полиэстер, 20% вискоза, 2% эластан",
 "material_ro":"78% poliester, 20% viscoză, 2% elastan",
 "fit":"Missy relaxed fit","length":"26 in / 66.04 cm",
 "neckline":"Curved V-neckline","sleeves":"Short sleeves",
 "pockets":"2 front patch pockets with instrument loops",
 "mesh_side_panels":True,"shirttail_hem":True,"fabric":"Silky stretch twill fabric",
 "supplier_visible_sizes":["2XS","XS","S","M","L","XL","2XL"]
}

LANG_BASE={
 "bg":{"name":"Дамска медицинска туника Cherokee WW Revolution WW601 Navy",
       "material":FACTS["material_bg"],
       "faq":[("Каква е материята?","78% полиестер, 20% вискоза и 2% еластан."),
              ("Каква е кройката?","Cherokee посочва Missy relaxed fit."),
              ("Колко джоба има?","Два предни външни джоба с примки за инструменти."),
              ("Има ли мрежести панели?","Да, има мрежести странични панели."),
              ("Каква е дължината?","26 инча, приблизително 66 cm."),
              ("Какви размери са наблюдавани?","2XS–2XL; това не доказва текуща наличност."),
              ("Какъв е кодът?","WW601; доказаният доставчик използва и WWE601."),
              ("Какво е деколтето?","Извито V-образно деколте.")]},
 "en":{"name":"Cherokee WW Revolution WW601 Navy Women's Scrub Top",
       "material":FACTS["material_raw"],
       "faq":[("What is the fabric composition?","78% polyester, 20% rayon and 2% spandex."),
              ("What fit does it have?","Cherokee specifies Missy relaxed fit."),
              ("How many pockets?","Two front patch pockets with instrument loops."),
              ("Does it have mesh panels?","Yes, mesh side panels."),
              ("What is the length?","26 inches, approximately 66 cm."),
              ("Which sizes were observed?","2XS–2XL; this does not certify current stock."),
              ("What is the style code?","WW601; exact supplier alias WWE601."),
              ("What neckline?","Curved V-neckline.")]},
 "ru":{"name":"Женская медицинская туника Cherokee WW Revolution WW601 Navy",
       "material":FACTS["material_ru"],
       "faq":[("Какой состав ткани?","78% полиэстер, 20% вискоза и 2% эластан."),
              ("Какая посадка?","Cherokee указывает Missy relaxed fit."),
              ("Сколько карманов?","Два передних кармана с петлями для инструментов."),
              ("Есть ли сетчатые панели?","Да, боковые сетчатые панели."),
              ("Какая длина?","26 дюймов, примерно 66 см."),
              ("Какие размеры наблюдались?","2XS–2XL; это не подтверждает текущий остаток."),
              ("Какой код модели?","WW601; поставщик использует WWE601."),
              ("Какой вырез?","Изогнутый V-образный.")]},
 "ro":{"name":"Bluză medicală damă Cherokee WW Revolution WW601 Navy",
       "material":FACTS["material_ro"],
       "faq":[("Care este compoziția?","78% poliester, 20% viscoză și 2% elastan."),
              ("Ce croială are?","Cherokee specifică Missy relaxed fit."),
              ("Câte buzunare are?","Două buzunare frontale cu bucle pentru instrumente."),
              ("Are panouri din plasă?","Da, panouri laterale din plasă."),
              ("Care este lungimea?","26 inch, aproximativ 66 cm."),
              ("Ce mărimi au fost observate?","2XS–2XL; nu confirmă stocul curent."),
              ("Care este codul modelului?","WW601; alias furnizor WWE601."),
              ("Ce tip de decolteu?","Decolteu curbat în V.")]}
}

INTENT_COPY={
 "commercial_product":{
  "bg":["Cherokee WW601 Navy – практичен избор за медицински специалисти","Фокусът е върху лесна оценка на продукта: материя, кройка, джобове, комфорт и размери."],
  "en":["Cherokee WW601 Navy – a practical choice for medical professionals","This version focuses on quick product evaluation: fabric, fit, pockets, comfort and sizes."],
  "ru":["Cherokee WW601 Navy — практичный выбор для медицинских специалистов","Акцент — на быстрой оценке товара: материал, посадка, карманы, комфорт и размеры."]},
 "technical_brand_catalogue":{
  "bg":["Технически профил на Cherokee WW601 Navy","Тази версия поставя на преден план проследимите спецификации, конструкцията и идентичността на модела."],
  "en":["Technical profile of Cherokee WW601 Navy","This version prioritizes traceable specifications, construction and canonical model identity."],
  "ru":["Технический профиль Cherokee WW601 Navy","Версия акцентирует подтвержденные характеристики, конструкцию и идентичность модели."]},
 "professional_workwear_search":{
  "bg":["Cherokee WW601 като професионално работно облекло","Тук моделът е представен през практичността за активна работа: свобода на движение, джобове и функционална конструкция."],
  "en":["Cherokee WW601 as professional workwear","This version emphasizes active-work practicality: mobility, storage and functional garment construction."],
  "ru":["Cherokee WW601 как профессиональная рабочая одежда","Акцент — на мобильности, карманах и функциональной конструкции для активной работы."]},
 "medical_professional":{
  "bg":["Cherokee WW601 за медицинска среда","Съдържанието е насочено към медицински и здравни специалисти, които оценяват комфорт, организация и професионален външен вид."],
  "en":["Cherokee WW601 for medical professionals","This presentation addresses medical and healthcare professionals seeking comfort, organization and a professional appearance."],
  "ru":["Cherokee WW601 для медицинских специалистов","Описание ориентировано на комфорт, организацию и профессиональный внешний вид в медицинской среде."]},
 "romanian_medical_commercial":{
  "ro":["Cherokee WW601 Navy pentru piața medicală din România","Prezentarea pune accent pe confort, buzunare, material elastic și o evaluare comercială clară a produsului."],
  "en":["Cherokee WW601 Navy for the Romanian medical market","The presentation emphasizes comfort, pockets, stretch fabric and clear commercial product evaluation."]},
 "romanian_professional_catalogue":{
  "ro":["Profil profesional Cherokee WW601 Navy","Această versiune pune accent pe date tehnice verificabile, croială și construcția produsului."],
  "en":["Professional catalogue profile for Cherokee WW601 Navy","This version emphasizes verifiable technical data, fit and garment construction."]}
}

def _common_sections(lang):
 if lang=="bg":
  return [("Материя и комфорт","Материята е 78% полиестер, 20% вискоза и 2% еластан. Cherokee я определя като silky stretch twill, а кройката е Missy relaxed fit."),
          ("Джобове и функционалност","Моделът има два предни джоба с примки за инструменти и мрежести странични панели."),
          ("Кройка и размер","Дължината по средата на гърба е 26 инча, приблизително 66 cm. При точния доставчиков продукт са наблюдавани размери 2XS–2XL; това не е твърдение за наличност."),
          ("Технически характеристики","Cherokee; WW Revolution; WW601; доставчиков alias WWE601; Navy; къси ръкави; извито V-образно деколте; shirttail долен край.")]
 if lang=="en":
  return [("Fabric and comfort","Fabric composition is 78% polyester, 20% rayon and 2% spandex. Cherokee describes it as silky stretch twill with a Missy relaxed fit."),
          ("Pockets and functionality","The style has two front patch pockets with instrument loops and mesh side panels."),
          ("Fit and sizes","Center-back length is 26 inches, approximately 66 cm. Sizes 2XS–2XL were observed on the exact supplier product; this is not a stock claim."),
          ("Technical specifications","Cherokee; WW Revolution; WW601; supplier alias WWE601; Navy; short sleeves; curved V-neckline; shirttail hem.")]
 if lang=="ru":
  return [("Материал и комфорт","Состав: 78% полиэстер, 20% вискоза и 2% эластан. Cherokee описывает ткань как silky stretch twill; посадка Missy relaxed fit."),
          ("Карманы и функциональность","Два передних кармана с петлями для инструментов и сетчатые боковые панели."),
          ("Посадка и размеры","Длина по центру спинки 26 дюймов, около 66 см. У точного товара поставщика наблюдались размеры 2XS–2XL; это не текущий остаток."),
          ("Технические характеристики","Cherokee; WW Revolution; WW601; alias поставщика WWE601; Navy; короткие рукава; V-образный вырез; shirttail край.")]
 if lang=="ro":
  return [("Material și confort","Compoziția este 78% poliester, 20% viscoză și 2% elastan. Cherokee descrie materialul drept silky stretch twill, cu Missy relaxed fit."),
          ("Buzunare și funcționalitate","Modelul are două buzunare frontale cu bucle pentru instrumente și panouri laterale din plasă."),
          ("Croială și mărimi","Lungimea centrală la spate este 26 inch, aproximativ 66 cm. La produsul exact al furnizorului au fost observate mărimile 2XS–2XL; aceasta nu este o afirmație de stoc."),
          ("Specificații tehnice","Cherokee; WW Revolution; WW601; alias furnizor WWE601; Navy; mâneci scurte; decolteu curbat în V; tiv shirttail.")]
 raise ValueError(lang)

def render_html(doc):
 parts=[f"<h1>{doc['h1']}</h1>",f"<p>{doc['short_description']}</p>"]
 for h,t in doc["sections"]:
  parts += [f"<h2>{h}</h2>",f"<p>{t}</p>"]
 faq_title={"bg":"Често задавани въпроси","en":"Frequently asked questions","ru":"Часто задаваемые вопросы","ro":"Întrebări frecvente"}[doc["language"]]
 parts.append(f"<h2>{faq_title}</h2>")
 for q,a in doc["faq"]:
  parts += [f"<h3>{q}</h3>",f"<p>{a}</p>"]
 return "\n".join(parts)

def build_document(site,lang):
 base=LANG_BASE[lang]; intent=CHANNELS[site]["intent"]; focus=INTENT_COPY[intent][lang]
 sections=[(focus[0],focus[1])] + _common_sections(lang)
 name=base["name"]
 meta_suffix=site.split(".")[0].upper()
 doc={
  "site":site,"language":lang,"channel_intent":intent,
  "name":name,"h1":name,
  "meta_title":f"{name.replace('WW Revolution ','')} | {meta_suffix}"[:70],
  "meta_description":focus[1][:160],
  "short_description":focus[1],
  "sections":sections,
  "faq":deepcopy(base["faq"]),
  "image_alt":[name,name+" V-neck",name+" pockets",name+" mesh panels",name+" Navy"],
  "keywords_entities":["Cherokee","WW Revolution","WW601","WWE601","Navy"],
  "schema_ready_facts":{"brand":"Cherokee","model":"WW601","color":"Navy","material":base["material"]},
  "claim_provenance":[
   {"source":"Cherokee manufacturer","authority":"AUTHORITATIVE","fields":["material","fit","length","neckline","sleeves","pockets","mesh_side_panels","shirttail_hem","fabric"]},
   {"source":"Stenso exact WWE601 Navy product","authority":"EXACT_SUPPLIER","fields":["supplier_alias","supplier_visible_sizes"],"stock_inference":False}
  ]
 }
 doc["long_description_html"]=render_html(doc)
 return doc

def normalize_text(html):
 return re.sub(r"\s+"," ",re.sub(r"<[^>]+>"," ",html)).strip().lower()

def similarity(a,b):
 return round(SequenceMatcher(None,normalize_text(a),normalize_text(b)).ratio(),4)

def build_all_sites_package():
 docs={}
 for site,cfg in CHANNELS.items():
  docs[site]={lang:build_document(site,lang) for lang in cfg["languages"]}

 comparisons=[]
 sites=list(CHANNELS)
 for i,a in enumerate(sites):
  for b in sites[i+1:]:
   common=set(CHANNELS[a]["languages"]) & set(CHANNELS[b]["languages"])
   for lang in common:
    score=similarity(docs[a][lang]["long_description_html"],docs[b][lang]["long_description_html"])
    comparisons.append({"site_a":a,"site_b":b,"language":lang,"similarity":score,"pass":score<0.90})

 publish_manifest={}
 for site,cfg in CHANNELS.items():
  publish_manifest[site]={
   "target_site":site,
   "platform":cfg["platform"],
   "mode":"WRITE_DRAFT",
   "required_languages":cfg["languages"],
   "active_after_write":False,
   "publish_live":False,
   "operator_confirmation_required":True,
   "adapter_status":"READY_BY_PLATFORM" if cfg["platform"] in ("prestashop_family","wordpress") else "BLOCKED_CONFIGURATION",
   "credential_env_hint":{
     "prestashop_family":"M99_"+site.upper().replace(".","_").replace("-","_")+"_API_KEY",
     "wordpress":"M99_"+site.upper().replace(".","_").replace("-","_")+"_APP_PASSWORD",
     "adapter_required":"CONFIGURE_CHANNEL_ADAPTER"
   }[cfg["platform"]]
  }

 return {
  "schema_version":VERSION,
  "mode":"ALL_SITES_CHANNEL_SPECIFIC_PUBLICATION_PACKAGE",
  "identity":IDENTITY,
  "channel_documents":docs,
  "similarity_guard":{"threshold":0.90,"comparisons":comparisons,"all_pass":all(x["pass"] for x in comparisons)},
  "publication_manifest":publish_manifest,
  "publication_policy":{
    "all_sites_required":True,
    "partial_success_is_failure":True,
    "write_mode":"WRITE_DRAFT",
    "active_after_write":False,
    "live_publish_allowed":False,
    "operator_confirmation_required":True,
    "price_auto_select":False,
    "stock_auto_claim":False
  }
 }
