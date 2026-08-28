from pathlib import Path
import importlib.util
import sys
import pytest

ROOT=Path(__file__).resolve().parents[1]
MOD=ROOT/"admin-platform/app/services/v073_phase45/source_registry_governance.py"

def load():
    spec=importlib.util.spec_from_file_location("source_registry_governance",MOD)
    m=importlib.util.module_from_spec(spec)
    # Python 3.14 dataclasses resolves postponed/string annotations through
    # sys.modules during class processing. Register the module before exec_module.
    sys.modules[spec.name]=m
    try:
        spec.loader.exec_module(m)
        return m
    except Exception:
        sys.modules.pop(spec.name,None)
        raise

def actors(m):
    return (
        m.Actor("op-1","Operator",False),
        m.Actor("sa-1","Super Admin",True),
    )

def test_operator_can_propose_but_proposal_is_not_operational():
    m=load();op,_=actors(m)
    p=m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="New Supplier",domain="https://example.com")
    assert p.status==m.ProposalStatus.PROPOSED
    assert p.operational is False
    assert p.visible_in_operator_registry is False

def test_only_superadmin_can_approve_or_reject():
    m=load();op,sa=actors(m)
    p=m.propose_source(actor=op,kind=m.SourceKind.MANUFACTURER,organization_name="Maker",domain="maker.example")
    with pytest.raises(m.GovernanceViolation,match="SUPERADMIN_REQUIRED"):
        m.review_source_proposal(actor=op,proposal=p,approve=True)
    m.review_source_proposal(actor=sa,proposal=p,approve=True)
    assert p.status==m.ProposalStatus.APPROVED

def test_rejected_is_hidden_but_can_be_reproposed_as_new_record():
    m=load();op,sa=actors(m)
    old=m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="A",domain="a.example")
    m.review_source_proposal(actor=sa,proposal=old,approve=False,reason="not enough evidence")
    assert old.visible_in_operator_registry is False
    new=m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="A",domain="a.example",rejected_history=[old])
    assert new.id!=old.id
    assert new.prior_rejected_proposal_id==old.id
    assert new.status==m.ProposalStatus.PROPOSED

def test_approved_duplicate_domain_is_blocked():
    m=load();op,sa=actors(m)
    p=m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="A",domain="a.example")
    m.review_source_proposal(actor=sa,proposal=p,approve=True)
    approved=m.approved_source_from_proposal(p)
    with pytest.raises(m.GovernanceViolation,match="SOURCE_ALREADY_APPROVED"):
        m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="A2",domain="https://www.a.example/x",approved_sources=[approved])

def test_only_superadmin_edits_domain_or_activation_and_history_is_preserved():
    m=load();op,sa=actors(m)
    p=m.propose_source(actor=op,kind=m.SourceKind.SUPPLIER,organization_name="A",domain="a.example")
    m.review_source_proposal(actor=sa,proposal=p,approve=True)
    s=m.approved_source_from_proposal(p)
    with pytest.raises(m.GovernanceViolation): m.edit_approved_source_domain(actor=op,source=s,new_domain="b.example")
    m.edit_approved_source_domain(actor=sa,source=s,new_domain="b.example")
    assert s.domain=="b.example" and "a.example" in s.previous_domains
    m.set_source_activation(actor=sa,source=s,active=False)
    assert s.activation==m.ActivationStatus.DEACTIVATED
    assert m.can_operator_use_source(s) is False

def test_any_operator_can_create_mapping_audit():
    m=load();op,_=actors(m)
    a=m.build_mapping_audit(actor=op,action="CREATE",supplier_product_id="sp-1",manufacturer_product_id="mp-9",previous_value=None)
    assert a.actor_user_id=="op-1"
    assert a.entity_type=="MANUFACTURER_SUPPLIER_PRODUCT_MAPPING"
    assert a.new_value=="mp-9"
    assert a.correlation_id

def test_category_mapping_only_to_approved_and_new_category_needs_superadmin():
    m=load();op,sa=actors(m)
    approved=m.CanonicalCategory("c1","Работни обувки",True)
    assert m.can_map_supplier_category(approved) is True
    p=m.propose_canonical_category(actor=op,name="Работни якета",approved_categories=[approved])
    with pytest.raises(m.GovernanceViolation): m.review_category_proposal(actor=op,proposal=p,approve=True)
    m.review_category_proposal(actor=sa,proposal=p,approve=True)
    assert p.status==m.CategoryProposalStatus.APPROVED

def test_rejected_category_can_be_reproposed_new_record():
    m=load();op,sa=actors(m)
    old=m.propose_canonical_category(actor=op,name="Нова категория")
    m.review_category_proposal(actor=sa,proposal=old,approve=False)
    new=m.propose_canonical_category(actor=op,name="Нова категория",rejected_history=[old])
    assert new.id!=old.id and new.prior_rejected_proposal_id==old.id

def test_bulk_default_selection_is_zero_and_never_direct_publish():
    m=load()
    x=m.bulk_selection_defaults(["p1","p2","p3"])
    assert x["discovered_count"]==3
    assert x["selected_count"]==0
    assert x["selected_ids"]==[]
    assert x["select_all_requires_explicit_operator_action"] is True
    assert x["direct_publish_allowed"] is False
