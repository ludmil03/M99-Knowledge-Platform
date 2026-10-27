from dataclasses import dataclass
@dataclass(frozen=True)
class LiveUIReadiness:
 authenticated:bool
 language_map:dict
 products_get:bool
 products_post_permission:bool
 products_put_permission:bool
 category_id:str
 schema_fields:int
 publish_enabled:bool=False
 write_allowed:bool=False
 write_performed:bool=False
def from_preflight(result):
 if result.get('write_performed') is not False or result.get('write_allowed') is not False:raise ValueError('PREFLIGHT_NOT_FAIL_CLOSED')
 lm=result.get('required_language_map') or {}
 if set(lm)!={'en','bg','ru'} or len(set(lm.values()))!=3:raise ValueError('LANGUAGE_MAP_INVALID')
 perms=result.get('products_permissions') or {}
 if not perms.get('get'):raise ValueError('PRODUCT_GET_REQUIRED')
 cat=result.get('test_category') or {};schema=result.get('blank_product_schema') or {}
 if not cat.get('id') or not schema.get('product_node'):raise ValueError('CATEGORY_OR_SCHEMA_INVALID')
 return LiveUIReadiness(result.get('api')=='AUTHENTICATED_HTTP_OK',dict(lm),True,bool(perms.get('post')),bool(perms.get('put')),str(cat['id']),int(schema.get('field_count',0)),False,False,False)
