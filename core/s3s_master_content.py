from __future__ import annotations


def build_s3s_content(facts: dict) -> dict:
    model = facts["model_name"]
    sizes = f"{facts['eu_sizes'][0]}–{facts['eu_sizes'][-1]}"

    bg = {
        "name": "Работни обувки Diadora Glove A.Box Low Pro S3S",
        "seo_title": f"Работни обувки Diadora {model}",
        "meta_description":
            f"Diadora {model}: S3S, алуминиево бомбе 200 J, "
            f"{facts['anti_puncture']}, ESD, FO HRO SR и размери EU {sizes}.",
        "short_description":
            f"Ниски защитни обувки Diadora {model}, клас S3S, "
            f"алуминиево бомбе 200 J, {facts['anti_puncture']} и ESD.",
        "long_description":
            f"Diadora {model} са ниски защитни обувки, класифицирани от "
            f"производителя като S3S. Моделът е с алуминиево защитно бомбе "
            f"200 J и система против пробиване {facts['anti_puncture']}. "
            f"Посочени са ESD характеристики, междинна подметка EVA и "
            f"външна подметка от нитрилен каучук с FO, HRO и SR. "
            f"Ширината е {facts['width']}, а официалният размерен диапазон "
            f"е EU {sizes}. Технологиите включват "
            f"{', '.join(facts['technology'])}.",
    }

    en = {
        "name": f"Diadora {model}",
        "seo_title": f"Diadora {model} Safety Shoes",
        "meta_description":
            f"Diadora {model}: S3S, 200 J aluminium toe cap, "
            f"{facts['anti_puncture']}, ESD, FO HRO SR and EU sizes {sizes}.",
        "short_description":
            f"Low-top Diadora {model} safety shoes, S3S, 200 J aluminium "
            f"toe cap, {facts['anti_puncture']} and ESD.",
        "long_description":
            f"Diadora {model} are low-top safety shoes classified by the "
            f"manufacturer as S3S. The model uses a 200 J aluminium safety "
            f"toe cap and {facts['anti_puncture']} anti-puncture system. "
            f"The manufacturer specifies ESD properties, an EVA midsole and "
            f"a nitrile-rubber outsole marked FO, HRO and SR. Width is "
            f"{facts['width']} and the official size range is EU {sizes}. "
            f"Technologies include {', '.join(facts['technology'])}.",
    }
    return {"bg": bg, "en": en}
