from .cache import *  # will also import some globals like `britive`


def test_access_builder_approvers_groups_create(cached_access_builder_approvers_groups):
    assert isinstance(cached_access_builder_approvers_groups, dict)
    assert isinstance(cached_access_builder_approvers_groups.get('id'), str)


def test_access_builder_approvers_groups_update(cached_access_builder_approvers_groups_update):
    assert isinstance(cached_access_builder_approvers_groups_update, dict)
    assert len(cached_access_builder_approvers_groups_update.get('members')) == 2


def test_access_builder_associations_create(cached_access_builder_associations):
    assert isinstance(cached_access_builder_associations, dict)
    assert isinstance(cached_access_builder_associations.get('associationApproversSummary'), list)
    assert isinstance(cached_access_builder_associations.get('associationApproversSummary')[0], dict)


def test_access_builder_associations_update(cached_access_builder_associations_update):
    assert isinstance(cached_access_builder_associations_update, dict)
    assert isinstance(cached_access_builder_associations_update.get('id'), str)
    assert len(cached_access_builder_associations_update.get('associations')) > 0


def test_access_builder_associations_list(cached_access_builder_associations_list):
    assert isinstance(cached_access_builder_associations_list, dict)
    assert isinstance(cached_access_builder_associations_list.get('associationApproversSummary'), list)
    assert len(cached_access_builder_associations_list['associationApproversSummary'][0].get('associations')) > 0
    assert len(cached_access_builder_associations_list['associationApproversSummary'][0].get('approversGroups')) > 0


def test_access_builder_requesters_add(cached_add_requesters_to_access_builder):
    assert isinstance(cached_add_requesters_to_access_builder, list)
    assert len(cached_add_requesters_to_access_builder) > 0
    assert isinstance(cached_add_requesters_to_access_builder[0], dict)


def test_add_notification_to_access_builder(cached_add_notification_to_access_builder):
    assert isinstance(cached_add_notification_to_access_builder, list)
    assert len(cached_add_notification_to_access_builder) > 0


def test_enable_access_requests(cached_enable_access_requests):
    assert isinstance(cached_enable_access_requests, dict)
    assert cached_enable_access_requests['allowAccessRequest']


def test_disable_access_requests(cached_disable_access_requests):
    assert isinstance(cached_disable_access_requests, dict)
    assert not cached_disable_access_requests['allowAccessRequest']
