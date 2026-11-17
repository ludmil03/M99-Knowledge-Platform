from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'admin-platform'))

from app.services.stage5_production_authorization import (
    AuthorizationPlan,
    build_authorization,
    validate_submission,
    validate_product_payload,
)


def plan(xml='<prestashop><product><name>Риза</name></product></prestashop>'):
    return build_authorization(
        identity_state='NEW', reference='M99 100020', target='m99.eu',
        gross_price='58.13', vat_rate='0.20', language_map={'bg': 2},
        content={'bg': {'name': 'Риза'}}, variants=[], payload_xml=xml,
        ready_targets=['m99.eu'],
    )


def submit(value, token=None):
    return validate_submission(
        value, submitted_token=token or value.scope_token,
        submitted_operation=value.operation,
        submitted_reference=value.reference, submitted_target=value.target,
    )


def test_changed_xml_changes_review_scope_even_when_product_facts_are_unchanged():
    original = plan()
    revised = plan('<prestashop><product><name>Риза</name><id_tax_rules_group>3</id_tax_rules_group></product></prestashop>')
    assert original.scope_token != revised.scope_token
    with pytest.raises(ValueError, match='SCOPE_TOKEN_MISMATCH'):
        submit(revised, original.scope_token)


def test_replacing_payload_without_review_is_rejected():
    with pytest.raises(ValueError, match='REVIEWED_PAYLOAD_CHANGED'):
        submit(replace(plan(), payload_xml='<changed/>'))


def test_replacing_payload_and_its_hash_cannot_reuse_original_review_scope():
    revised_xml = '<changed/>'
    tampered = replace(plan(), payload_xml=revised_xml,
                       payload_sha256=sha256(revised_xml.encode()).hexdigest())
    with pytest.raises(ValueError, match='REVIEWED_SCOPE_CHANGED'):
        submit(tampered)


def test_old_session_plans_require_a_fresh_review():
    original = plan()
    legacy = AuthorizationPlan(original.operation, original.reference,
                               original.target, original.scope_token, original.payload_xml)
    with pytest.raises(ValueError, match='REVIEWED_PAYLOAD_CHANGED'):
        submit(legacy)


@pytest.mark.parametrize('changes', [
    {'operation': 'UPDATE'}, {'reference': 'M99 100021'}, {'target': 'mela99.com'},
])
def test_changed_plan_descriptors_cannot_reuse_reviewed_token(changes):
    with pytest.raises(ValueError, match='REVIEWED_SCOPE_CHANGED'):
        submit(replace(plan(), **changes))


def test_reviewed_utf8_payload_survives_session_serialization():
    original = plan()
    assert submit(AuthorizationPlan(**asdict(original)))
    assert plan().scope_token == original.scope_token


def live_xml():
    localized = ''.join(
        '<{0}><language id="2">Проверен текст</language></{0}>'.format(field)
        for field in ('name', 'description', 'description_short', 'meta_title', 'meta_description')
    )
    return ('<prestashop><product><reference>M99 100020</reference>'
            '<price>48.441667</price><id_category_default>26</id_category_default>'
            '<id_tax_rules_group>3</id_tax_rules_group><active>0</active>'
            '<available_for_order>0</available_for_order><visibility>none</visibility>'
            + localized + '</product></prestashop>')


def test_complete_create_and_exact_existing_update_payloads():
    assert validate_product_payload(plan(live_xml()))
    update_xml = live_xml().replace('<product>', '<product><id>2042</id>')
    update = replace(plan(update_xml), operation='UPDATE')
    assert validate_product_payload(update, remote_id='2042')
    with pytest.raises(ValueError, match='UPDATE_PAYLOAD_REMOTE_ID_MISMATCH'):
        validate_product_payload(update, remote_id='2041')


@pytest.mark.parametrize('old,new,error', [
    ('M99 100020', 'M99 100021', 'REFERENCE_MISMATCH'),
    ('<price>48.441667</price>', '<price>NaN</price>', 'PRICE_INVALID'),
    ('<price>48.441667</price>', '<price>0</price>', 'PRICE_INVALID'),
    ('<id_tax_rules_group>3', '<id_tax_rules_group>0', 'POSITIVE_ID_REQUIRED'),
    ('<active>0</active>', '', 'FIELD_REQUIRED:active'),
    ('<visibility>none', '<visibility>unknown', 'VISIBILITY_INVALID'),
    ('<product>', '<product><id>2042</id>', 'CREATE_PAYLOAD_MUST_NOT_HAVE_ID'),
    ('<reference>M99 100020</reference>', '<reference>M99 100020</reference><reference>M99 100020</reference>', 'FIELD_REQUIRED:reference'),
    ('<meta_title><language id="2">', '<meta_title><language id="7">', 'LANGUAGE_SET_MISMATCH'),
    ('<meta_title><language id="2">Проверен текст</language></meta_title>', '<meta_title/>', 'LANGUAGE_SET_MISMATCH'),
])
def test_invalid_live_payload_is_rejected_before_any_network(old, new, error, monkeypatch):
    from app.services import stage5_final_ui_publish as publisher

    candidate = plan(live_xml().replace(old, new))
    calls = []
    monkeypatch.setattr(publisher, 'resolve_reference', lambda *args: calls.append(args))
    with pytest.raises(ValueError, match=error):
        publisher.execute_ui_publish(
            cfg=None, plan=candidate, submitted_token=candidate.scope_token,
            submitted_operation=candidate.operation, submitted_reference=candidate.reference,
            submitted_target=candidate.target, operator_confirmed=True,
        )
    assert calls == []
