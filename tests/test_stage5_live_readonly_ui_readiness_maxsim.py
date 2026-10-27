import pytest
from app.services.stage5_live_ui_readiness import *
def R():
 return {'api':'AUTHENTICATED_HTTP_OK','required_language_map':{'en':'7','bg':'4','ru':'9'},'products_permissions':{'get':True,'post':True,'put':True,'delete':False},'test_category':{'id':'26'},'blank_product_schema':{'product_node':True,'field_count':70},'write_performed':False,'write_allowed':False}
def test_view_fail_closed():
 x=from_preflight(R());assert x.authenticated and x.language_map=={'en':'7','bg':'4','ru':'9'} and not x.publish_enabled and not x.write_allowed and not x.write_performed
def test_permission_does_not_enable_write():
 r=R();r['products_permissions']['post']=True;r['products_permissions']['put']=True;x=from_preflight(r);assert x.products_post_permission and x.products_put_permission and not x.publish_enabled
def test_bad_map_blocks():
 r=R();r['required_language_map']={'en':'1','bg':'1','ru':'3'}
 with pytest.raises(ValueError):from_preflight(r)
def test_non_failclosed_preflight_blocks():
 r=R();r['write_allowed']=True
 with pytest.raises(ValueError):from_preflight(r)
