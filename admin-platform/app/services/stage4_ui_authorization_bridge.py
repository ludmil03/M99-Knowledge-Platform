from dataclasses import dataclass
import hashlib,json
@dataclass(frozen=True)
class PublishPreview:
 source:str;targets:tuple[str,...];selection_mode:str;product_refs:tuple[str,...];scope_token:str;publish_enabled:bool=False;write_performed:bool=False
def build_publish_preview(draft,stage3):
 raw={'source':draft.source_name or '','targets':list(draft.ready_targets),'selection_mode':draft.selection_mode or '','product_refs':list(draft.selected_product_refs)}
 token=hashlib.sha256(json.dumps(raw,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode('utf-8')).hexdigest()
 return PublishPreview(raw['source'],tuple(raw['targets']),raw['selection_mode'],tuple(raw['product_refs']),token,False,False)
def verify_preview_scope(preview,submitted_token):return bool(submitted_token) and preview.scope_token==submitted_token
