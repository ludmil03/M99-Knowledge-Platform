def build_claim_trace(canonical):
    return [{
        "claim_key":key,
        "claim_value":item["value"],
        "evidence_source":item["source"],
        "evidence_field":item["source_field"],
        "confidence":item["confidence"],
        "status":"SUPPORTED",
    } for key,item in canonical["facts"].items()]
