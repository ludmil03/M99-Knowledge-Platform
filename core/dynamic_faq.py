def _sizes(f):
    return f"{f['eu_sizes'][0]}–{f['eu_sizes'][-1]}"

def build_dynamic_faq(f, language, profile=None):
    s=_sizes(f)
    if language=="bg":
        items=[
          {"fact_keys":["protection_class"],"q":"Какъв е класът на защита?","a":f"Производителят класифицира модела като {f['protection_class']}."},
          {"fact_keys":["toe_cap"],"q":"Какво защитно бомбе използва моделът?","a":"Моделът е с алуминиево защитно бомбе 200 J."},
          {"fact_keys":["anti_puncture"],"q":"Каква е защитата от пробиване?","a":f"Производителят посочва {f['anti_puncture']}."},
          {"fact_keys":["esd"],"q":"Моделът има ли ESD характеристики?","a":"Да, производителят посочва ESD за този модел."},
          {"fact_keys":["outsole"],"q":"Какви характеристики има външната подметка?","a":"Външната подметка е от нитрилен каучук с обозначения FO, HRO и SR."},
          {"fact_keys":["eu_sizes"],"q":"Какъв е размерният диапазон?","a":f"Официално посочените размери са EU {s}."},
        ]
    elif language=="ro":
        items=[
          {"fact_keys":["protection_class"],"q":"Care este clasa de protecție?","a":f"Producătorul clasifică modelul în clasa {f['protection_class']}."},
          {"fact_keys":["toe_cap"],"q":"Ce tip de bombeu de protecție are?","a":"Modelul are bombeu de protecție din aluminiu, 200 J."},
          {"fact_keys":["anti_puncture"],"q":"Ce protecție antiperforație este specificată?","a":f"Producătorul specifică {f['anti_puncture']}."},
          {"fact_keys":["esd"],"q":"Modelul are proprietăți ESD?","a":"Da, producătorul specifică proprietăți ESD pentru acest model."},
          {"fact_keys":["outsole"],"q":"Ce caracteristici are talpa exterioară?","a":"Talpa exterioară este din cauciuc nitrilic și este marcată FO, HRO și SR."},
          {"fact_keys":["eu_sizes"],"q":"Care este gama de mărimi?","a":f"Mărimile indicate de producător sunt EU {s}."},
        ]
    else:
        items=[
          {"fact_keys":["protection_class"],"q":"What is the protection class?","a":f"The manufacturer classifies the model as {f['protection_class']}."},
          {"fact_keys":["toe_cap"],"q":"What toe protection is specified?","a":"The model uses a 200 J aluminium safety toe cap."},
          {"fact_keys":["anti_puncture"],"q":"What anti-puncture protection is specified?","a":f"The manufacturer specifies {f['anti_puncture']}."},
          {"fact_keys":["esd"],"q":"Does the model have ESD properties?","a":"Yes. The manufacturer specifies ESD properties for this model."},
          {"fact_keys":["outsole"],"q":"What outsole properties are specified?","a":"The nitrile-rubber outsole is marked FO, HRO and SR."},
          {"fact_keys":["eu_sizes"],"q":"What is the EU size range?","a":f"Manufacturer-listed sizes are EU {s}."},
        ]
    return [x for x in items if all(k in f and f[k] not in (None,"",[]) for k in x["fact_keys"])]
