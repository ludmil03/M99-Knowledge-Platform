from app.services.stage5_ui_live_preflight_bridge import *
def R():return {'api':'AUTHENTICATED_HTTP_OK','required_language_map':{'en':'7','bg':'4','ru':'9'},'products_permissions':{'get':True,'post':True,'put':True,'delete':False},'test_category':{'id':'26'},'blank_product_schema':{'product_node':True,'field_count':70},'write_performed':False,'write_allowed':False}
def test_locked():
 x=build_live_preflight_view(R());assert x['credential']=='PRESENT_NOT_PRINTED' and not x['publish_enabled'] and not x['write_allowed'] and not x['write_performed']
