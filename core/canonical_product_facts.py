from dataclasses import dataclass, asdict

@dataclass(frozen=True)
class CanonicalFact:
    key: str
    value: object
    source: str
    source_field: str
    confidence: str = "VERIFIED"

REQUIRED_KEYS = (
    "model_name","manufacturer_item","colour","protection_class","product_type",
    "upper","toe_cap","anti_puncture","width","lining","insole","esd",
    "midsole","outsole","eu_sizes"
)

def build_canonical_product_facts(manufacturer_name, manufacturer_url, manufacturer_facts):
    missing=[k for k in REQUIRED_KEYS if manufacturer_facts.get(k) in (None,"",[])]
    if missing:
        raise ValueError("Missing verified manufacturer facts: "+", ".join(missing))
    facts={}
    for key in REQUIRED_KEYS:
        facts[key]=CanonicalFact(key,manufacturer_facts[key],manufacturer_name,key)
    if manufacturer_facts.get("technology"):
        facts["technology"]=CanonicalFact("technology",manufacturer_facts["technology"],manufacturer_name,"technology")
    return {
        "status":"VERIFIED",
        "source_url":manufacturer_url,
        "facts":{k:asdict(v) for k,v in facts.items()}
    }

def canonical_values(canonical):
    return {k:v["value"] for k,v in canonical["facts"].items()}
