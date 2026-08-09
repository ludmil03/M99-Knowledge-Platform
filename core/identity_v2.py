from dataclasses import dataclass
import re
from typing import Optional, Any

M99_ID_PATTERN = re.compile(r"^M99 [0-9]{6}$")

def format_m99_id(number:int)->str:
    if number < 1 or number > 999999:
        raise ValueError("M99 sequence out of range")
    return f"M99 {number:06d}"

def validate_m99_id(value:str)->bool:
    return bool(M99_ID_PATTERN.fullmatch(value or ""))

@dataclass
class ChannelIdentity:
    channel_id:str
    external_product_id:Optional[str]=None
    external_variant_id:Optional[str]=None
    reference:Optional[str]=None
    canonical_url:Optional[str]=None
    url_protected:bool=True
    match_status:str="unconfirmed"

    def validate_update(self,new_data:dict[str,Any])->list[str]:
        errors=[]
        if self.url_protected and self.canonical_url:
            u=new_data.get("canonical_url")
            if u and u != self.canonical_url:
                errors.append("canonical_url is protected")
        pid=new_data.get("external_product_id")
        if self.external_product_id and pid and pid != self.external_product_id:
            errors.append("external_product_id is immutable")
        return errors
