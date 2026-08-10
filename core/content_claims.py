"""Claim policy for v0.6.4.1.

The content layer may rephrase verified manufacturer facts, but it must not invent
comparative, performance, suitability or superlative marketing claims.
"""

CLAIM_TYPES = ("FACT", "DERIVED_SAFE_CLAIM", "MARKETING_CLAIM", "UNSUPPORTED_CLAIM")

# Derived claims below are deliberately narrow and trace back to canonical facts.
DERIVED_SAFE_CLAIMS = {
    "low_cut": {
        "requires": ("product_type",),
        "evidence_contains": "low-top",
        "bg": "ниска конструкция",
        "en": "low-cut construction",
        "ro": "construcție joasă",
    },
    "breathable_upper": {
        "requires": ("upper",),
        "evidence_contains": "breathable",
        "bg": "дишаща горна част",
        "en": "breathable upper",
        "ro": "parte superioară respirabilă",
    },
    "removable_insole": {
        "requires": ("insole",),
        "evidence_contains": "removable",
        "bg": "подвижна стелка",
        "en": "removable insole",
        "ro": "branț detașabil",
    },
}

FORBIDDEN_MARKETING_PATTERNS = (
    "по-леко от", "по-лека от", "по-леки от", "най-лек", "най-добър", "най-добра",
    "lighter than", "lightest", "best in class", "best-in-class", "superior to",
    "mai ușor decât", "cea mai bună", "cel mai bun", "superior față de",
    "целодневен комфорт", "all-day comfort", "confort pe tot parcursul zilei",
)

def build_claim_policy(canonical_facts):
    derived=[]
    for key, rule in DERIVED_SAFE_CLAIMS.items():
        field=rule["requires"][0]
        value=str(canonical_facts.get(field, "")).lower()
        if rule["evidence_contains"].lower() in value:
            derived.append({
                "claim_key":key,
                "claim_type":"DERIVED_SAFE_CLAIM",
                "derived_from":[field],
                "status":"SUPPORTED",
                "text":{"bg":rule["bg"],"en":rule["en"],"ro":rule["ro"]},
            })
    return {
        "allowed_types":["FACT","DERIVED_SAFE_CLAIM"],
        "review_types":["MARKETING_CLAIM"],
        "blocked_types":["UNSUPPORTED_CLAIM"],
        "derived_safe_claims":derived,
        "marketing_claim_rule":"Marketing/comparative/performance claims require explicit evidence before use.",
    }

def find_forbidden_marketing_claims(text):
    t=str(text).lower()
    return [p for p in FORBIDDEN_MARKETING_PATTERNS if p.lower() in t]
