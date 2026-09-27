from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ChannelPolicy:
    key: str
    kind: str
    authorized: bool
    ready: bool
    platform: str
    note: str = ""

CHANNEL_POLICIES: tuple[ChannelPolicy,...] = (
    ChannelPolicy("mela99.com","CHANNEL",True,True,"Thirty Bees / PS-compatible"),
    ChannelPolicy("rabotni-drehi.com","CHANNEL",True,True,"WordPress"),
    ChannelPolicy("m99.eu","CHANNEL",True,True,"PrestaShop 9","Adapter verified"),
    ChannelPolicy("medicinski-drehi.com","CHANNEL",True,True,"WordPress"),
    ChannelPolicy("laviro.ro","CHANNEL",True,True,"PrestaShop 1.6"),
    ChannelPolicy("alviro.ro","CHANNEL",True,False,"UNPROVEN","Requires readiness proof"),
    ChannelPolicy("toplinka.com","CHANNEL",True,False,"WordPress + WooCommerce",
                  "Authorized channel; readiness must be proven before write"),
    ChannelPolicy("dolibarr","ERP",True,False,"Dolibarr","ERP write contract not ready"),
)

def channel_policy(key:str)->ChannelPolicy|None:
    return next((x for x in CHANNEL_POLICIES if x.key==key),None)
