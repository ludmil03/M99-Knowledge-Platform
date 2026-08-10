CHANNEL_CONTENT_PROFILES = {
    "mela99.com": {
        "positioning":"authoritative_product_catalogue",
        "languages":["bg","en"],
        "content_order":["identity","protection","construction","comfort_facts","specifications","faq"],
        "tone":"technical_commercial",
    },
    "m99.eu": {
        "positioning":"professional_international",
        "languages":["bg","en"],
        "content_order":["professional_context","verified_protection","technology","materials","specifications","faq"],
        "tone":"professional_technical",
    },
    "rabotni-drehi.com": {
        "positioning":"transactional_search",
        "languages":["bg"],
        "content_order":["use_case","key_protection","practical_construction","sizes","specifications","faq"],
        "tone":"practical_transactional",
    },
    "laviro.ro": {
        "positioning":"romanian_transactional_search",
        "languages":["ro"],
        "content_order":["use_case","protection","materials","construction","specifications","faq"],
        "tone":"natural_romanian_transactional",
    },
}

def get_channel_profile(channel):
    return CHANNEL_CONTENT_PROFILES[channel]
