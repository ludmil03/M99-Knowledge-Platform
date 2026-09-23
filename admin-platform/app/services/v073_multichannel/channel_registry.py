CHANNELS=[
{"channel_id":"m99.eu","platform":"prestashop","version":"9.1.5","role":"STORE"},
{"channel_id":"mela99.com","platform":"thirtybees","version":"1.7.0","role":"STORE"},
{"channel_id":"medicinski-drehi.com","platform":"prestashop","version":"1.7.8.11","role":"STORE"},
{"channel_id":"rabotni-drehi.com","platform":"woocommerce","version":"WordPress 7.0.5 / Enfold","role":"STORE"},
{"channel_id":"laviro.ro","platform":"prestashop","version":"1.6.1.24","role":"STORE"},
{"channel_id":"alviro.ro","platform":"thirtybees","version":"1.1.0-1.1.x","role":"STORE"},
{"channel_id":"toplinka.com","platform":"woocommerce","version":"WordPress 7.1 / Enfold Child","role":"STORE"},
{"channel_id":"dolibarr","platform":"dolibarr","version":"20.0.2","role":"ERP"}]
for c in CHANNELS:c.update(replaceable_platform=True,replaceable_version=True,mutation_allowed=False,adapter_mode="READ_ONLY_PREFLIGHT")
def get(i):return next(dict(c) for c in CHANNELS if c["channel_id"]==i)
