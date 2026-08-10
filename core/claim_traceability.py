def build_claim_trace(canonical, claim_policy=None):
    trace=[{
        "claim_key":key,
        "claim_value":item["value"],
        "claim_type":"FACT",
        "derived_from":[],
        "evidence_source":item["source"],
        "evidence_field":item["source_field"],
        "confidence":item["confidence"],
        "status":"SUPPORTED",
    } for key,item in canonical["facts"].items()]
    if claim_policy:
        for item in claim_policy.get("derived_safe_claims",[]):
            trace.append({
                "claim_key":item["claim_key"],
                "claim_value":item["text"],
                "claim_type":"DERIVED_SAFE_CLAIM",
                "derived_from":item["derived_from"],
                "evidence_source":"canonical_product_facts",
                "evidence_field":",".join(item["derived_from"]),
                "confidence":"DERIVED_FROM_VERIFIED_FACT",
                "status":"SUPPORTED",
            })
    return trace
