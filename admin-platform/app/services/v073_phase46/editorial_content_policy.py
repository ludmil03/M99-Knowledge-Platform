from __future__ import annotations

EDITORIAL_POLICY_ID = "CONTENT-EDITORIAL-001"
EDITORIAL_POLICY_STATUS = "DECIDED"
EDITORIAL_POLICY_VERSION = 1

POLICY = {
    "authoring_mode": "MODEL_ASSISTED_ALLOWED",
    "detector_evasion_objective": False,
    "knowledge_first": True,
    "ai_native_not_ai_invented": True,
    "supplier_prose_verbatim": False,
    "channel_specific": True,
    "language_specific": True,
    "heading_rule": "H2_H5_ONLY_WHEN_SEMANTICALLY_NEEDED",
    "required_quality_gates": (
        "FACTUAL_EVIDENCE_COVERAGE",
        "SEO_SEARCH_INTENT_FIT",
        "BOILERPLATE_SIMILARITY",
        "CROSS_PRODUCT_SIMILARITY",
        "LANGUAGE_NATURALNESS",
        "META_SHORT_DISTINCTNESS",
        "CLAIM_SUPPORT",
    ),
}

def policy_preview() -> dict:
    return {
        "policy_id": EDITORIAL_POLICY_ID,
        "status": EDITORIAL_POLICY_STATUS,
        "version": EDITORIAL_POLICY_VERSION,
        **POLICY,
    }
