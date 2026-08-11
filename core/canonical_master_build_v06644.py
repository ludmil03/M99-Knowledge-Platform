from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def pick_nonempty(*values):
    for v in values:
        if isinstance(v, str) and v.strip():
            return v.strip()
        if v not in (None, "", [], {}):
            return v
    return None


def canonical_identity() -> dict:
    return {
        "m99_productgroup_id": "M99 100017",
        "brand": "Diadora Utility",
        "model_name": "GLOVE A.BOX LOW PRO S3S",
        "manufacturer_item": "701.183119_80013",
        "protection_class": "S3S",
        "colour": "BLACK",
    }


def manufacturer_facts() -> dict:
    # Evidence already established in the M99 project for this exact item.
    return {
        "source_type": "manufacturer",
        "source_name": "Diadora Utility",
        "source_url": "https://www.diadorautility.com/en/bg/glove_a.box_low_pro_s3s/701.183119_80013.html",
        "identity_strength": "authoritative_exact_item",
        "facts": {
            "model_name": "GLOVE A.BOX LOW PRO S3S",
            "manufacturer_item": "701.183119_80013",
            "colour": "BLACK",
            "protection_class": "S3S",
            "product_type": "low-top safety shoes",
            "toe_cap": "aluminium 200J",
            "anti_puncture": "K SOLE",
            "esd": True,
            "technology": ["A.Box System", "K SOLE"],
        },
    }


def build_bg_content(identity: dict, facts: dict) -> dict:
    model = identity["model_name"]
    long_html = f"""
<h2>Работни обувки Diadora {model}</h2>
<p><strong>Diadora {model}</strong> са ниски защитни обувки клас <strong>S3S</strong>,
предназначени за професионална употреба. Каноничната идентичност на този продукт
е свързана с производствен код <strong>{identity['manufacturer_item']}</strong>.</p>

<h2>Защита и стандарт S3S</h2>
<p>Моделът е класифициран като <strong>S3S</strong>. Производителят посочва
алуминиево защитно бомбе с устойчивост 200 J и система за защита от пробиване
<strong>{facts['anti_puncture']}</strong>.</p>

<h2>Конструкция и технологии</h2>
<h3>A.Box System</h3>
<p>A.Box System е технология, посочена от Diadora Utility за този модел.</p>
<h3>{facts['anti_puncture']}</h3>
<p>Системата е част от защитната конструкция на обувката.</p>

<h2>ESD и професионална употреба</h2>
<p>Моделът е обозначен като ESD и е предназначен за работни среди, в които се
изисква сертифицирана защитна обувка.</p>

<h2>Технически характеристики</h2>
<ul>
<li>Марка: Diadora Utility</li>
<li>Модел: {model}</li>
<li>Производствен код: {identity['manufacturer_item']}</li>
<li>Защитен клас: S3S</li>
<li>Цвят: BLACK</li>
<li>Бомбе: алуминиево, 200 J</li>
<li>Защита от пробиване: {facts['anti_puncture']}</li>
<li>ESD: да</li>
</ul>

<h2>Често задавани въпроси</h2>
<h3>Какъв е класът на защита?</h3>
<p>Моделът е S3S.</p>
<h3>Има ли защитно бомбе?</h3>
<p>Да. Производителят посочва алуминиево бомбе 200 J.</p>
<h3>Има ли защита от пробиване?</h3>
<p>Да. Използвана е система {facts['anti_puncture']}.</p>
<h3>Подходящ ли е моделът за ESD среда?</h3>
<p>Да, моделът е обозначен като ESD.</p>
""".strip()

    return {
        "name": f"Работни обувки Diadora GLOVE A.BOX LOW PRO S3S",
        "h1": f"Работни обувки Diadora GLOVE A.BOX LOW PRO S3S",
        "meta_title": "Работни обувки Diadora GLOVE A.BOX LOW PRO S3S | M99",
        "meta_description": "Diadora GLOVE A.BOX LOW PRO S3S – защитни обувки S3S с алуминиево бомбе 200 J, защита от пробиване K SOLE и ESD.",
        "short_description": "Ниски защитни обувки Diadora Utility GLOVE A.BOX LOW PRO S3S с алуминиево бомбе 200 J, K SOLE и ESD.",
        "long_description_html": long_html,
    }


def build_en_content(identity: dict, facts: dict) -> dict:
    model = identity["model_name"]
    long_html = f"""
<h2>Diadora {model} safety shoes</h2>
<p><strong>Diadora {model}</strong> are low-top <strong>S3S</strong> safety shoes
for professional use. The canonical product identity is linked to manufacturer
item <strong>{identity['manufacturer_item']}</strong>.</p>

<h2>S3S protection</h2>
<p>The model is classified as <strong>S3S</strong>. Diadora Utility specifies a
200 J aluminium toe cap and <strong>{facts['anti_puncture']}</strong>
anti-puncture protection.</p>

<h2>Construction and technologies</h2>
<h3>A.Box System</h3>
<p>A.Box System is listed by Diadora Utility for this model.</p>
<h3>{facts['anti_puncture']}</h3>
<p>This system is part of the protective construction of the footwear.</p>

<h2>ESD and professional use</h2>
<p>The model is specified as ESD and is intended for professional environments
requiring certified safety footwear.</p>

<h2>Technical specifications</h2>
<ul>
<li>Brand: Diadora Utility</li>
<li>Model: {model}</li>
<li>Manufacturer item: {identity['manufacturer_item']}</li>
<li>Safety class: S3S</li>
<li>Colour: BLACK</li>
<li>Toe cap: aluminium, 200 J</li>
<li>Anti-puncture: {facts['anti_puncture']}</li>
<li>ESD: yes</li>
</ul>

<h2>Frequently asked questions</h2>
<h3>What is the protection class?</h3>
<p>The model is classified as S3S.</p>
<h3>Does it have a safety toe cap?</h3>
<p>Yes. Diadora specifies a 200 J aluminium toe cap.</p>
<h3>Does it have anti-puncture protection?</h3>
<p>Yes. It uses {facts['anti_puncture']} protection.</p>
<h3>Is it suitable for ESD environments?</h3>
<p>Yes, the model is specified as ESD.</p>
""".strip()

    return {
        "name": f"Diadora GLOVE A.BOX LOW PRO S3S safety shoes",
        "h1": f"Diadora GLOVE A.BOX LOW PRO S3S safety shoes",
        "meta_title": "Diadora GLOVE A.BOX LOW PRO S3S Safety Shoes | M99",
        "meta_description": "Diadora GLOVE A.BOX LOW PRO S3S safety shoes with S3S protection, 200 J aluminium toe cap, K SOLE anti-puncture protection and ESD.",
        "short_description": "Low-top Diadora Utility GLOVE A.BOX LOW PRO S3S safety shoes with 200 J aluminium toe cap, K SOLE and ESD.",
        "long_description_html": long_html,
    }


def build_master_preview(live_2076: dict, live_2100: dict, live_meta: dict) -> dict:
    identity = canonical_identity()
    mf = manufacturer_facts()
    facts = mf["facts"]

    # Container choice is deliberately not finalized here.
    container = {
        "selected_product_id": None,
        "candidate_product_ids": ["2076", "2100"],
        "operator_selection_required": True,
        "reason": "content quality and canonical container are evaluated separately",
    }

    categories_2076 = live_2076.get("associations", {}).get("categories", [])
    categories_2100 = live_2100.get("associations", {}).get("categories", [])
    images_2076 = live_2076.get("associations", {}).get("images", [])
    images_2100 = live_2100.get("associations", {}).get("images", [])
    combos_2076 = live_2076.get("associations", {}).get("combinations", [])
    combos_2100 = live_2100.get("associations", {}).get("combinations", [])

    reference_2076 = live_2076.get("scalar_fields", {}).get("reference") or None
    reference_2100 = live_2100.get("scalar_fields", {}).get("reference") or None

    proposed = {
        "identity": identity,
        "reference": {
            "proposed": identity["m99_productgroup_id"],
            "operator_approval_required": True,
            "legacy_candidates": [
                x for x in [reference_2076, reference_2100] if x
            ],
        },
        "languages": live_meta["languages"],
        "review_category": live_meta["review_category"],
        "content": {
            "bg": build_bg_content(identity, facts),
            "en": build_en_content(identity, facts),
        },
        "assets": {
            "images": {
                "2076_count": len(images_2076),
                "2100_count": len(images_2100),
                "strategy": "KEEP_BEST_PROVEN_SET_AFTER_OPERATOR_REVIEW",
            },
            "combinations": {
                "2076_count": len(combos_2076),
                "2100_count": len(combos_2100),
                "strategy": "PRESERVE_PROVEN_VARIANTS; NO_AUTOMATIC_RENUMBERING",
            },
        },
        "categories": {
            "2076": categories_2076,
            "2100": categories_2100,
            "strategy": "PRESERVE_VALID_EXISTING_CATEGORIES_PLUS_DISCOVERED_TEST_DURING_REVIEW",
        },
        "commercial": {
            "price": {
                "2076": live_2076.get("scalar_fields", {}).get("price"),
                "2100": live_2100.get("scalar_fields", {}).get("price"),
                "proposed": None,
                "operator_approval_required": True,
            },
            "tax_rules_group": {
                "2076": live_2076.get("scalar_fields", {}).get("id_tax_rules_group"),
                "2100": live_2100.get("scalar_fields", {}).get("id_tax_rules_group"),
                "proposed": None,
                "operator_review_required": True,
            },
        },
    }

    provenance = [
        {
            "field": "identity.model_name",
            "source": "Diadora Utility authoritative exact item",
            "proposed": identity["model_name"],
            "reason": "canonical manufacturer identity",
        },
        {
            "field": "identity.manufacturer_item",
            "source": "Diadora Utility authoritative exact item",
            "proposed": identity["manufacturer_item"],
            "reason": "exact manufacturer item",
        },
        {
            "field": "content.bg",
            "source": "M99 regenerated from manufacturer evidence",
            "proposed": "NEW",
            "reason": "both existing products have incomplete SEO/content structure",
        },
        {
            "field": "content.en",
            "source": "M99 regenerated from manufacturer evidence",
            "proposed": "NEW",
            "reason": "existing EN naming/content is inconsistent",
        },
        {
            "field": "reference",
            "source": "M99 canonical identity",
            "proposed": identity["m99_productgroup_id"],
            "reason": "channel reference must converge to canonical M99 identity after approval",
        },
    ]

    return {
        "schema_version": "0.6.6.4.4",
        "mode": "CANONICAL_MASTER_BUILD_PREVIEW_ONLY",
        "writes": {"channels": False, "dolibarr": False, "supplier": False},
        "container": container,
        "manufacturer_evidence": mf,
        "proposed_master": proposed,
        "provenance": provenance,
        "decision_gates": {
            "container_product_id_selected": False,
            "price_approved": False,
            "tax_approved": False,
            "reference_migration_approved": False,
            "content_approved": False,
            "write_allowed": False,
        },
    }
