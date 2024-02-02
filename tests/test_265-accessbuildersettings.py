from .cache import *  # will also import some globals like `britive`


def test_create(cached_accesbuilder_settings):
    assert isinstance(cached_accesbuilder_settings, dict)
    assert isinstance(cached_accesbuilder_settings.get('id'), str)


def test_update_approver_group(cached_accessbuilder_settings_update):
    print(cached_accessbuilder_settings_update)
    assert isinstance(cached_accessbuilder_settings_update, dict)
    assert len(cached_accessbuilder_settings_update.get('members')) == 2


def test_list_approver_group(cached_accesbuilder_settings, cached_application):
    approver_groups = britive.access_builder.approvers_groups.list(application_id=cached_application['appContainerId'])
    assert isinstance(approver_groups, dict)
    assert isinstance(approver_groups.get('approversGroupSummary'), list)
    assert len(approver_groups.get('approversGroupSummary')) == 1


def test_access_builder_association_create(cached_access_builder_associations):
    assert isinstance(cached_access_builder_associations, dict)
    assert isinstance(cached_access_builder_associations.get('id'), str)


def test_access_builder_association_update(cached_access_builder_associations_update):
    assert isinstance(cached_access_builder_associations_update, dict)
    assert isinstance(cached_access_builder_associations_update.get('id'), str)
    assert len(cached_access_builder_associations_update.get('associations')) > 0


def test_access_builder_association_list(cached_access_builder_associations_update,
                                         cached_application):
    Asscns = britive.access_builder.associations.list(application_id=cached_application['appContainerId'])
    assert isinstance(Asscns, dict)
    assert isinstance(Asscns.get('associationApproversSummary'), list)
    assert len(Asscns.get('associationApproversSummary')) > 0


def test_access_builder_requesters_add(cached_add_requesters_to_access_builder):
    assert isinstance(cached_add_requesters_to_access_builder, list)
    assert len(cached_add_requesters_to_access_builder) > 0
    assert isinstance(cached_add_requesters_to_access_builder[0], dict)


def test_add_notification_to_access_builder(cached_add_notification_to_access_builder):
    assert isinstance(cached_add_notification_to_access_builder, list)
    assert len(cached_add_notification_to_access_builder) > 0


def test_enable_access_builder_settings(cached_enable_access_requests):
    assert isinstance(cached_enable_access_requests, dict)
    assert cached_enable_access_requests.get('allowAccessRequests') == True


def test_cached_disable_access_requests(cached_enable_access_requests):
    assert isinstance(cached_enable_access_requests, dict)
    assert cached_enable_access_requests.get('allowAccessRequests') == False
