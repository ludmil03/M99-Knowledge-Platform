def _sizes(f):
    return f"{f['eu_sizes'][0]}–{f['eu_sizes'][-1]}"

def _common_bg(f):
    s=_sizes(f)
    return {
        "class":{"fact_keys":["protection_class"],"q":"Какъв е класът на защита?","a":f"Производителят класифицира модела като {f['protection_class']}."},
        "toe":{"fact_keys":["toe_cap"],"q":"Какво защитно бомбе използва моделът?","a":"Моделът е с алуминиево защитно бомбе 200 J."},
        "puncture":{"fact_keys":["anti_puncture"],"q":"Имат ли обувките защита от пробиване?","a":f"Производителят посочва {f['anti_puncture']} като система за защита от пробиване."},
        "esd":{"fact_keys":["esd"],"q":"Моделът има ли ESD характеристики?","a":"Да, производителят посочва ESD за този модел."},
        "outsole":{"fact_keys":["outsole"],"q":"Какви характеристики има външната подметка?","a":"Външната подметка е от нитрилен каучук с обозначения FO, HRO и SR."},
        "sizes":{"fact_keys":["eu_sizes"],"q":"Какъв е размерният диапазон?","a":f"Официално посочените размери са EU {s}."},
        "width":{"fact_keys":["width"],"q":"Каква ширина е посочена за модела?","a":f"Производителят посочва ширина {f['width']}."},
        "upper":{"fact_keys":["upper"],"q":"От какви материали е горната част?","a":"Горната част е от велурена телешка кожа и дишаща мрежа от 100% рециклиран полиестер."},
    }

def _common_en(f):
    s=_sizes(f)
    return {
        "class":{"fact_keys":["protection_class"],"q":"What is the protection class?","a":f"The manufacturer classifies the model as {f['protection_class']}."},
        "toe":{"fact_keys":["toe_cap"],"q":"What toe protection is specified?","a":"The model uses a 200 J aluminium safety toe cap."},
        "puncture":{"fact_keys":["anti_puncture"],"q":"What anti-puncture protection is specified?","a":f"The manufacturer specifies {f['anti_puncture']}."},
        "esd":{"fact_keys":["esd"],"q":"Does the model have ESD properties?","a":"Yes. The manufacturer specifies ESD properties for this model."},
        "outsole":{"fact_keys":["outsole"],"q":"What outsole properties are specified?","a":"The nitrile-rubber outsole is marked FO, HRO and SR."},
        "sizes":{"fact_keys":["eu_sizes"],"q":"What is the EU size range?","a":f"Manufacturer-listed sizes are EU {s}."},
        "width":{"fact_keys":["width"],"q":"What width is specified for the model?","a":f"The manufacturer specifies width {f['width']}."},
        "upper":{"fact_keys":["upper"],"q":"What materials are used in the upper?","a":"The upper combines cowhide suede with breathable 100% recycled polyester mesh."},
    }

def _common_ro(f):
    s=_sizes(f)
    return {
        "class":{"fact_keys":["protection_class"],"q":"Care este clasa de protecție?","a":f"Producătorul clasifică modelul în clasa {f['protection_class']}."},
        "toe":{"fact_keys":["toe_cap"],"q":"Ce tip de bombeu de protecție are?","a":"Modelul are bombeu de protecție din aluminiu, 200 J."},
        "puncture":{"fact_keys":["anti_puncture"],"q":"Ce protecție antiperforație este specificată?","a":f"Producătorul specifică {f['anti_puncture']}."},
        "esd":{"fact_keys":["esd"],"q":"Modelul are proprietăți ESD?","a":"Da, producătorul specifică proprietăți ESD pentru acest model."},
        "outsole":{"fact_keys":["outsole"],"q":"Ce caracteristici are talpa exterioară?","a":"Talpa exterioară este din cauciuc nitrilic și este marcată FO, HRO și SR."},
        "sizes":{"fact_keys":["eu_sizes"],"q":"Care este gama de mărimi?","a":f"Mărimile indicate de producător sunt EU {s}."},
        "width":{"fact_keys":["width"],"q":"Ce lățime este indicată pentru model?","a":f"Producătorul indică lățimea {f['width']}."},
        "upper":{"fact_keys":["upper"],"q":"Din ce materiale este realizată partea superioară?","a":"Partea superioară combină pielea întoarsă de bovină cu plasă respirabilă din poliester 100% reciclat."},
    }

def build_dynamic_faq(f, language, profile=None):
    positioning=(profile or {}).get("positioning","")
    if language=="ro":
        pool=_common_ro(f)
        order=["class","puncture","esd","upper","outsole","sizes"]
    elif language=="en":
        pool=_common_en(f)
        if positioning=="professional_international":
            order=["class","esd","width","upper","outsole","sizes"]
        else:
            order=["class","toe","puncture","esd","outsole","sizes"]
    else:
        pool=_common_bg(f)
        if positioning=="professional_international":
            order=["class","esd","width","upper","outsole","sizes"]
        elif positioning=="transactional_search":
            order=["class","puncture","esd","width","outsole","sizes"]
        else:
            order=["class","toe","puncture","esd","outsole","sizes"]
    items=[pool[k] for k in order]
    return [x for x in items if all(k in f and f[k] not in (None,"",[]) for k in x["fact_keys"])]
