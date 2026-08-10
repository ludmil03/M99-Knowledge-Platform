def _sizes(f):
    return f"{f['eu_sizes'][0]}–{f['eu_sizes'][-1]}"

def _specs_bg(f):
    return {
        "Клас на защита":f["protection_class"],
        "Защитно бомбе":"Алуминиево, 200 J",
        "Защита от пробиване":f["anti_puncture"],
        "Горна част":"Велурена телешка кожа и дишаща мрежа от 100% рециклиран полиестер",
        "Подплата":"Polyester Air Mesh с противоплъзгаща вложка от микрофибър",
        "Стелка":"Подвижна анатомична микроперфорирана стелка от PU пяна с активен въглен",
        "Междинна подметка":"EVA",
        "Външна подметка":"Нитрилен каучук, FO HRO SR",
        "Ширина":str(f["width"]),
        "ESD":"Да" if f["esd"] else "Не",
        "Цвят":"Черен" if str(f["colour"]).upper()=="BLACK" else str(f["colour"]),
        "Размери EU":_sizes(f)
    }

def _specs_en(f):
    return {
        "Protection class":f["protection_class"],
        "Toe cap":"Aluminium, 200 J",
        "Anti-puncture":f["anti_puncture"],
        "Upper":"Cowhide suede and breathable 100% recycled polyester mesh",
        "Lining":"Polyester Air Mesh with non-slip microfibre insert",
        "Insole":"Removable anatomical micro-perforated open-cell PU foam with activated carbon",
        "Midsole":"EVA",
        "Outsole":"Nitrile rubber, FO HRO SR",
        "Width":str(f["width"]),
        "ESD":"Yes" if f["esd"] else "No",
        "Colour":str(f["colour"]).title(),
        "EU sizes":_sizes(f)
    }

def _specs_ro(f):
    return {
        "Clasa de protecție":f["protection_class"],
        "Bombeu":"Aluminiu, 200 J",
        "Protecție antiperforație":f["anti_puncture"],
        "Partea superioară":"Piele întoarsă de bovină și plasă respirabilă din poliester 100% reciclat",
        "Căptușeală":"Polyester Air Mesh cu inserție antialunecare din microfibră",
        "Branț":"Anatomic, detașabil, microperforat, din spumă PU cu carbon activ",
        "Talpă intermediară":"EVA",
        "Talpă exterioară":"Cauciuc nitrilic, FO HRO SR",
        "Lățime":str(f["width"]),
        "ESD":"Da" if f["esd"] else "Nu",
        "Culoare":"Negru" if str(f["colour"]).upper()=="BLACK" else str(f["colour"]),
        "Mărimi EU":_sizes(f)
    }

def _bg_mela(f):
    m,s=f["model_name"],_sizes(f)
    return {
      "seo_title":f"Работни обувки Diadora {m} | MELA99",
      "meta_description":f"Diadora {m}: клас {f['protection_class']}, алуминиево бомбе 200 J, K SOLE Ultralite, ESD и размери EU {s}.",
      "h1":f"Работни обувки Diadora {m}",
      "short_description":f"Ниски защитни обувки Diadora Utility, клас {f['protection_class']}, с алуминиево бомбе 200 J, K SOLE Ultralite и ESD.",
      "long_description":f"Diadora Utility {m} е нисък защитен модел с горна част от велурена телешка кожа и дишаща мрежа от 100% рециклиран полиестер. Защитата включва алуминиево бомбе 200 J и система K SOLE Ultralite. Моделът е с ширина {f['width']}, технологии A.Box System и Ariatex, подплата Air Mesh и подвижна анатомична микроперфорирана стелка от PU пяна с активен въглен. Междинната подметка е EVA, а външната подметка е от нитрилен каучук с характеристики FO HRO SR. Официалният размерен диапазон е EU {s}.",
      "h2":[f"Защита {f['protection_class']} и ESD","Материали и технологии","Комфорт и конструкция","Размери и технически характеристики"],
      "faq":[
        {"q":"Какъв е класът на защита?","a":f"Производителят класифицира модела като {f['protection_class']}."},
        {"q":"Какво защитно бомбе използва моделът?","a":"Алуминиево защитно бомбе с устойчивост 200 J."},
        {"q":"Какъв е размерният диапазон?","a":f"Размери EU {s}."}
      ],
      "image_alt":[f"Diadora {m} черни защитни обувки",f"Diadora {m} страничен изглед",f"Подметка на Diadora {m} FO HRO SR"],
      "specifications":_specs_bg(f)
    }

def _en_mela(f):
    m,s=f["model_name"],_sizes(f)
    return {
      "seo_title":f"Diadora {m} Safety Shoes | MELA99",
      "meta_description":f"Diadora {m}: {f['protection_class']}, 200 J aluminium toe cap, K SOLE Ultralite, ESD and EU sizes {s}.",
      "h1":f"Diadora {m} Safety Shoes",
      "short_description":f"Low-cut Diadora Utility safety footwear with {f['protection_class']} protection, a 200 J aluminium toe cap, K SOLE Ultralite and ESD.",
      "long_description":f"Diadora Utility {m} combines a cowhide suede upper with breathable 100% recycled polyester mesh. Protection includes a 200 J aluminium toe cap and K SOLE Ultralite. The design uses width {f['width']}, A.Box System and Ariatex, Air Mesh lining and a removable anatomical micro-perforated PU foam insole with activated carbon. The midsole is EVA and the outsole is nitrile rubber with FO HRO SR properties. Manufacturer-listed EU sizes: {s}.",
      "h2":[f"{f['protection_class']} and ESD protection","Upper materials and technologies","Comfort and construction","EU sizes and specifications"],
      "faq":[
        {"q":"What is the protection class?","a":f"The manufacturer classifies the model as {f['protection_class']}."},
        {"q":"What toe protection is used?","a":"A 200 J aluminium safety toe cap."},
        {"q":"What is the EU size range?","a":f"EU {s}."}
      ],
      "image_alt":[f"Diadora {m} black safety shoes",f"Diadora {m} side view",f"Diadora {m} FO HRO SR outsole"],
      "specifications":_specs_en(f)
    }

def _bg_m99(f):
    c=_bg_mela(f); m,s=f["model_name"],_sizes(f)
    c.update({
      "seo_title":f"Diadora {m} професионални обувки | M99.eu",
      "h1":f"Diadora {m} – професионални защитни обувки",
      "short_description":f"Професионални обувки Diadora Utility с клас {f['protection_class']}, ESD, A.Box System и размери EU {s}.",
      "long_description":f"Diadora Utility {m} е професионален нисък модел за работни среди, в които са необходими защита на пръстите, защита от пробиване и ESD. Горната част съчетава велурена телешка кожа и дишаща мрежа от рециклиран полиестер. Моделът използва алуминиево бомбе 200 J, K SOLE Ultralite, A.Box System и Ariatex. Подметката комбинира EVA междинен слой и нитрилен каучук с FO HRO SR. Размери EU {s}."
    })
    return c

def _en_m99(f):
    c=_en_mela(f); m,s=f["model_name"],_sizes(f)
    c.update({
      "seo_title":f"Diadora {m} Professional Footwear | M99.eu",
      "h1":f"Diadora {m} Professional Safety Footwear",
      "short_description":f"Professional Diadora Utility footwear with {f['protection_class']}, ESD, A.Box System and EU sizes {s}.",
      "long_description":f"Diadora Utility {m} is low-cut professional safety footwear with a suede-and-mesh upper, a 200 J aluminium toe cap, K SOLE Ultralite and ESD properties. A.Box System and Ariatex support the upper construction, while the sole package combines EVA and nitrile rubber with FO HRO SR properties. Listed EU sizes: {s}."
    })
    return c

def _bg_rabotni(f):
    c=_bg_mela(f); m,s=f["model_name"],_sizes(f)
    c.update({
      "seo_title":f"Защитни обувки Diadora {m} | Работни дрехи",
      "h1":f"Защитни обувки Diadora {m}",
      "short_description":f"Diadora {m} за професионална работа: {f['protection_class']}, ESD, алуминиево бомбе 200 J и K SOLE Ultralite.",
      "long_description":f"За работна среда, в която са важни защитата и дишащата конструкция, Diadora {m} предлага горна част от велурена телешка кожа и рециклирана полиестерна мрежа. Защитният пакет включва алуминиево бомбе 200 J и K SOLE Ultralite. A.Box System и Ariatex допълват конструкцията, а Air Mesh подплатата и анатомичната PU стелка с активен въглен са предназначени за продължително професионално носене. Размери EU {s}."
    })
    return c

def _ro_laviro(f):
    m,s=f["model_name"],_sizes(f)
    return {
      "seo_title":f"Pantofi de protecție Diadora {m} | Laviro",
      "meta_description":f"Diadora {m}: clasa {f['protection_class']}, bombeu din aluminiu 200 J, K SOLE Ultralite, ESD și mărimi EU {s}.",
      "h1":f"Pantofi de protecție Diadora {m}",
      "short_description":f"Încălțăminte joasă Diadora Utility, clasa {f['protection_class']}, cu bombeu din aluminiu 200 J, K SOLE Ultralite și ESD.",
      "long_description":f"Diadora Utility {m} combină pielea întoarsă de bovină cu plasă respirabilă din poliester 100% reciclat. Protecția include un bombeu din aluminiu 200 J și K SOLE Ultralite. Construcția folosește lățimea {f['width']}, A.Box System și Ariatex, căptușeală Air Mesh și un branț anatomic detașabil, microperforat, din spumă PU cu carbon activ. Talpa intermediară este EVA, iar talpa exterioară este din cauciuc nitrilic cu caracteristici FO HRO SR. Mărimi EU: {s}.",
      "h2":[f"Protecție {f['protection_class']} și ESD","Materiale și tehnologii","Confort și construcție","Mărimi și specificații"],
      "faq":[
        {"q":"Care este clasa de protecție?","a":f"Producătorul clasifică modelul ca {f['protection_class']}."},
        {"q":"Ce tip de bombeu are?","a":"Bombeu de protecție din aluminiu, 200 J."},
        {"q":"Care este gama de mărimi?","a":f"EU {s}."}
      ],
      "image_alt":[f"Pantofi de protecție negri Diadora {m}",f"Diadora {m} vedere laterală",f"Talpă Diadora {m} FO HRO SR"],
      "specifications":_specs_ro(f)
    }

def build_diadora_content_preview(product):
    return {
      "mela99.com":{"bg":_bg_mela(product),"en":_en_mela(product)},
      "m99.eu":{"bg":_bg_m99(product),"en":_en_m99(product)},
      "rabotni-drehi.com":{"bg":_bg_rabotni(product)},
      "laviro.ro":{"ro":_ro_laviro(product)}
    }
