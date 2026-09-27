from app.services.channel_registry_governance import CHANNEL_POLICIES,channel_policy
def test_toplinka_is_authorized_but_not_ready():
    p=channel_policy("toplinka.com")
    assert p is not None and p.authorized is True and p.ready is False
    assert p.platform=="WordPress + WooCommerce"
def test_all_expected_destinations_present():
    keys={p.key for p in CHANNEL_POLICIES}
    assert keys=={"mela99.com","rabotni-drehi.com","m99.eu","medicinski-drehi.com","laviro.ro","alviro.ro","toplinka.com","dolibarr"}
def test_no_policy_silently_makes_unproven_channels_ready():
    assert channel_policy("alviro.ro").ready is False
    assert channel_policy("toplinka.com").ready is False
    assert channel_policy("dolibarr").ready is False
