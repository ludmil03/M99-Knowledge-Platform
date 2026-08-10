from __future__ import annotations
from copy import deepcopy


def _base_facts(product: dict) -> dict:
    required = (
        "model_name", "manufacturer_item", "colour", "protection_class",
        "upper", "toe_cap", "anti_puncture", "width", "lining",
        "insole", "midsole", "outsole", "eu_sizes",
    )
    missing = [k for k in required if not product.get(k)]
    if missing:
        raise ValueError(
            "Verified manufacturer facts missing: " + ", ".join(missing)
        )
    return product


def build_diadora_content_preview(product: dict) -> dict:
    f = _base_facts(product)
    model = f["model_name"]
    sizes = f"{f['eu_sizes'][0]}–{f['eu_sizes'][-1]}"

    # Each site owns its wording. The technical fact set is shared,
    # but prose is intentionally not copied verbatim between channels.
    mela_bg = {
        "seo_title": f"Работни обувки Diadora {model} | MELA99",
        "meta_description": (
            f"Diadora {model} S1PS: алуминиево бомбе 200J, "
            f"K SOLE Ultralite, ESD, A.Box System и размери {sizes}."
        ),
        "h1": f"Работни обувки Diadora {model}",
        "short_description": (
            f"Ниски защитни обувки Diadora {model}, клас {f['protection_class']}, "
            f"с алуминиево бомбе 200J, текстилна защита от пробиване и ESD."
        ),
        "long_description": (
            f"{model} е нисък защитен модел на Diadora Utility с горна част от "
            f"велурена телешка кожа и дишаща рециклирана полиестерна мрежа. "
            f"Защитата включва {f['toe_cap']} и {f['anti_puncture']}. "
            f"Конструкцията е ширина {f['width']}, с A.Box System и Ariatex, "
            f"Air Mesh подплата и анатомична подвижна стелка от PU пяна с "
            f"активен въглен. Междинната подметка е {f['midsole']}, а външната "
            f"е {f['outsole']}. Наличният размерен диапазон по данни на "
            f"производителя е EU {sizes}."
        ),
        "h2": [
            "Защита и стандарт S1PS",
            "Материали и вентилация",
            "Комфорт при продължително носене",
            "Размери и избор на номер",
        ],
        "faq": [
            {
                "q": "Какъв клас на защита има моделът?",
                "a": f"Производителят обозначава този exact item като {f['protection_class']}."
            },
            {
                "q": "Има ли метално бомбе?",
                "a": "Моделът е с алуминиево защитно бомбе 200J."
            },
            {
                "q": "Какви размери се предлагат?",
                "a": f"Официалният диапазон е EU {sizes}."
            },
        ],
        "image_alt": [
            f"Diadora {model} черни работни обувки",
            f"Diadora {model} S1PS страничен изглед",
            f"Подметка Diadora {model} FO HRO SR",
        ],
    }

    mela_en = {
        "seo_title": f"Diadora {model} S1PS Safety Shoes | MELA99",
        "meta_description": (
            f"Diadora {model}: 200J aluminium toe cap, K SOLE Ultralite, "
            f"ESD, A.Box System and EU sizes {sizes}."
        ),
        "h1": f"Diadora {model} S1PS Safety Shoes",
        "short_description": (
            f"Low-cut Diadora Utility safety footwear with {f['toe_cap']}, "
            f"{f['anti_puncture']}, ESD construction and width {f['width']}."
        ),
        "long_description": (
            f"{model} combines a cowhide suede upper with breathable recycled "
            f"polyester mesh. Protection is provided by the {f['toe_cap']} and "
            f"{f['anti_puncture']}. The shoe uses A.Box System and Ariatex, "
            f"Air Mesh lining and a removable anatomical PU foam insole with "
            f"activated carbon. The midsole is {f['midsole']} and the outsole "
            f"is {f['outsole']}. Manufacturer-listed EU sizes: {sizes}."
        ),
        "h2": [
            "S1PS protection",
            "Breathable upper and A.Box technology",
            "Footbed and underfoot comfort",
            "EU size range",
        ],
        "faq": [
            {"q": "What is the protection class?", "a": f"The exact manufacturer item is listed as {f['protection_class']}."},
            {"q": "What toe protection is used?", "a": "A 200J aluminium toe cap."},
            {"q": "Which EU sizes are listed?", "a": f"EU {sizes}."},
        ],
        "image_alt": [
            f"Diadora {model} black safety shoes",
            f"Diadora {model} S1PS side view",
            f"Diadora {model} FO HRO SR outsole",
        ],
    }

    m99_bg = deepcopy(mela_bg)
    m99_bg.update({
        "seo_title": f"Diadora {model} S1PS професионални обувки | M99.eu",
        "h1": f"Diadora {model} – професионални защитни обувки S1PS",
        "short_description": (
            f"Професионален Diadora Utility модел за работа, комбиниращ "
            f"S1PS защита, ESD, A.Box System и размери EU {sizes}."
        ),
        "long_description": (
            f"Diadora Utility {model} е професионален нисък модел за среди, "
            f"в които са нужни защита на пръстите, устойчивост на пробиване и "
            f"контролирано разсейване на електростатичен заряд. Горната част "
            f"съчетава велурена телешка кожа и дишаща рециклирана полиестерна "
            f"мрежа. Използвани са {f['toe_cap']}, {f['anti_puncture']}, "
            f"A.Box System, Ariatex и подметка {f['outsole']}. "
            f"Размери по данни на производителя: EU {sizes}."
        ),
    })

    m99_en = deepcopy(mela_en)
    m99_en.update({
        "seo_title": f"Diadora {model} Professional S1PS Footwear | M99.eu",
        "h1": f"Diadora {model} Professional S1PS Footwear",
        "short_description": (
            f"Professional Diadora Utility footwear with S1PS protection, "
            f"ESD, A.Box System and manufacturer-listed EU sizes {sizes}."
        ),
        "long_description": (
            f"Diadora Utility {model} is designed as low-cut professional "
            f"safety footwear with a suede-and-mesh upper, {f['toe_cap']}, "
            f"{f['anti_puncture']} and ESD properties. A.Box System with "
            f"Ariatex supports breathability, while the sole package combines "
            f"{f['midsole']} with {f['outsole']}. Listed EU sizes: {sizes}."
        ),
    })

    rabotni_bg = deepcopy(mela_bg)
    rabotni_bg.update({
        "seo_title": f"Защитни обувки Diadora {model} S1PS | Работни дрехи",
        "h1": f"Защитни обувки Diadora {model} S1PS",
        "short_description": (
            f"Diadora {model} за професионална употреба: S1PS, ESD, "
            f"алуминиево бомбе и K SOLE Ultralite."
        ),
        "long_description": (
            f"За работна среда, в която защитата трябва да се съчетае с "
            f"дишане и нисък профил, {model} използва горна част от велур и "
            f"рециклирана полиестерна мрежа. Защитният пакет включва "
            f"{f['toe_cap']} и {f['anti_puncture']}. A.Box System и Ariatex "
            f"подпомагат въздухообмена, а Air Mesh подплатата и анатомичната "
            f"стелка са насочени към комфорт при продължително носене. "
            f"Размери: EU {sizes}."
        ),
    })

    laviro_ro = {
        "seo_title": f"Pantofi de protecție Diadora {model} S1PS | Laviro",
        "meta_description": (
            f"Diadora {model} S1PS cu bombeu din aluminiu 200J, "
            f"K SOLE Ultralite, ESD, A.Box System și mărimi EU {sizes}."
        ),
        "h1": f"Pantofi de protecție Diadora {model} S1PS",
        "short_description": (
            f"Încălțăminte de protecție joasă Diadora Utility, clasa "
            f"{f['protection_class']}, cu bombeu din aluminiu 200J și ESD."
        ),
        "long_description": (
            f"{model} combină pielea întoarsă de bovină cu plasă respirabilă "
            f"din poliester reciclat. Protecția include {f['toe_cap']} și "
            f"{f['anti_puncture']}. Sistemele A.Box și Ariatex susțin "
            f"respirabilitatea, iar căptușeala Air Mesh și branțul anatomic "
            f"detașabil din spumă PU cu carbon activ contribuie la confort. "
            f"Talpa intermediară este {f['midsole']}, iar talpa exterioară "
            f"este {f['outsole']}. Mărimi EU declarate de producător: {sizes}."
        ),
        "h2": [
            "Protecție S1PS",
            "Materiale și respirabilitate",
            "Confort și susținere",
            "Gama de mărimi EU",
        ],
        "faq": [
            {"q": "Care este clasa de protecție?", "a": f"Articolul exact al producătorului este clasificat {f['protection_class']}."},
            {"q": "Ce tip de bombeu are?", "a": "Bombeu din aluminiu, rezistență declarată 200J."},
            {"q": "Ce mărimi sunt disponibile în gama producătorului?", "a": f"EU {sizes}."},
        ],
        "image_alt": [
            f"Pantofi de protecție Diadora {model} negri",
            f"Diadora {model} S1PS vedere laterală",
            f"Talpă Diadora {model} FO HRO SR",
        ],
    }

    return {
        "mela99.com": {"bg": mela_bg, "en": mela_en},
        "m99.eu": {"bg": m99_bg, "en": m99_en},
        "rabotni-drehi.com": {"bg": rabotni_bg},
        "laviro.ro": {"ro": laviro_ro},
    }
