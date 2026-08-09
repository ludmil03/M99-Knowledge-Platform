OWNERSHIP={
 "m99_id":("M99",{"M99"}),
 "product_identity":("M99",{"M99"}),
 "stock":("DOLIBARR",{"DOLIBARR"}),
 "pmp":("DOLIBARR",{"DOLIBARR"}),
 "seo_content":("M99",{"M99"}),
 "canonical_url":("CHANNEL",{"CHANNEL"}),
 "legacy_id":("SOURCE",set()),
 "channel_product_id":("CHANNEL",set()),
}
def can_write(field:str,actor:str)->bool:
    return actor in OWNERSHIP.get(field,("",set()))[1]
