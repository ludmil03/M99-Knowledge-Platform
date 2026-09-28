from decimal import Decimal
import pytest
from app.services.stage4_publish_boundary import *
def C():
 return {x:{"name":"N","short":"S","long":"L","meta_title":"T","meta_description":"D"} for x in ("en","bg","ru")}
def P(**k):
 d=dict(identity_state="NEW",m99_id=None,canonical_name="UNO LOW",gross_price=Decimal("58.13"),vat_rate=Decimal("20"),content=C(),variants=("36","37","38"),target="m99.eu");d.update(k);return PublishProduct(**d)
def test_new_create_requires_collision_checked_id_at_boundary():
 x=build_publish_payload(P(),new_m99_id="M99 100019");assert x.operation=="CREATE" and x.reference=="M99 100019"
def test_existing_update_reuses_id():
 x=build_publish_payload(P(identity_state="EXISTING",m99_id="M99 100018"));assert x.operation=="UPDATE" and x.reference=="M99 100018"
def test_bad_id_and_missing_language_and_duplicate_variant_block():
 with pytest.raises(ValueError):build_publish_payload(P(),new_m99_id="M99-123")
 c=C();del c["ru"]
 with pytest.raises(ValueError):build_publish_payload(P(content=c),new_m99_id="M99 100019")
 with pytest.raises(ValueError):build_publish_payload(P(variants=("36","36")),new_m99_id="M99 100019")
def test_unproven_channel_adapter_blocks():
 with pytest.raises(ValueError,match="ADAPTER_NOT_PROVEN"):build_publish_payload(P(target="mela99.com"),new_m99_id="M99 100019")
def test_ps9_simulated_create_update_readback():
 a=SimulatedPS9Adapter([])
 for p in (build_publish_payload(P(),new_m99_id="M99 100019"),build_publish_payload(P(identity_state="EXISTING",m99_id="M99 100018"))):
  r=a.create(p) if p.operation=="CREATE" else a.update(p);assert a.readback(p,r)
 assert [x[0] for x in a.calls]==["POST","GET","PUT","GET"]
