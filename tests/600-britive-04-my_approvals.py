from contextlib import ExitStack

from .cache import *  # will also import some globals like `britive`


@pytest.mark.skipif(scan_skip, reason=scan_skip_message)
def test_approval(cached_profile_checkout_request):
    request_id = cached_profile_checkout_request['requestId']

    response = britive.my_approvals.reject_request(request_id=request_id)

    assert response is None

    approvals = britive.my_approvals.list()
    approval = next(a for a in approvals if a['requestId'] == request_id)
    assert approval['status'] == 'REJECTED'


def test_list_filters():
    approvals = britive.my_approvals.list(created_within_days=7, active_status='all')
    assert isinstance(approvals, list)


@pytest.fixture(scope='module')
def approval_setup():
    me = britive.my_access.whoami()
    suffix = int(time() * 1_000_000)
    catalog = {app['key']: app for app in britive.application_management.applications.catalog()}
    with ExitStack() as cleanup:
        application = britive.application_management.applications.create(
            catalog_id=catalog['AWS Standalone-1.0']['catalogAppId'], application_name=f'pysdktest-approvals-{suffix}'
        )
        cleanup.callback(britive.application_management.applications.delete, application['appContainerId'])
        environment = britive.application_management.environments.create(
            application_id=application['appContainerId'], name=f'pysdktest-approvals-{suffix}'
        )
        profile = britive.application_management.profiles.create(
            application_id=application['appContainerId'], name=f'pysdktest-approvals-{suffix}'
        )
        service_identity = britive.identity_management.service_identities.create(
            name=f'pysdktest-approvals-{suffix}', status='active'
        )
        cleanup.callback(britive.identity_management.service_identities.delete, service_identity['userId'])
        token = britive.identity_management.service_identity_tokens.create(service_identity['userId'], 1)
        policy = britive.application_management.profiles.policies.build(
            name=f'pysdktest-approvals-{suffix}',
            service_identities=[service_identity['name']],
            approval_notification_medium='Email',
            approver_users=[me['username']],
        )
        britive.application_management.profiles.policies.create(profile_id=profile['papId'], policy=policy)
        requester = Britive(tenant=britive.tenant, token=token['token'], query_features=False)
        cleanup.callback(requester.session.close)
        yield {
            'me': me,
            'profile_id': profile['papId'],
            'environment_id': environment['id'],
            'requester': requester,
        }


@pytest.fixture
def pending_request(approval_setup):
    requester = approval_setup['requester']
    request = requester.my_access.request_approval(
        profile_id=approval_setup['profile_id'],
        environment_id=approval_setup['environment_id'],
        justification='pysdktest approval lifecycle',
    )
    request_id = request['requestId']
    yield request_id
    if requester.my_requests.approval_request_status(request_id=request_id)['status'] == 'PENDING':
        requester.my_requests.withdraw_approval_request(request_id=request_id)


def _status(setup, request_id):
    return setup['requester'].my_requests.approval_request_status(request_id=request_id)['status']


def test_get_approvers(approval_setup):
    approvers = approval_setup['requester'].my_access.get_approvers(profile_id=approval_setup['profile_id'])
    assert approval_setup['me']['userId'] in [u['id'] for u in approvers['approvers']['users']]


def test_request_is_listed(approval_setup, pending_request):
    mine = [r for r in approval_setup['requester'].my_requests.list() if r['requestId'] == pending_request]
    assert mine and mine[0]['status'] == 'PENDING'
    pending = britive.my_approvals.list(filter_text='status eq PENDING')
    assert pending_request in [a['requestId'] for a in pending]
    recent = britive.my_approvals.list(active_status='all', created_within_days=1)
    assert pending_request in [a['requestId'] for a in recent]


def test_get(approval_setup, pending_request):
    request = britive.my_approvals.get(request_id=pending_request)
    assert request['requestId'] == pending_request
    assert request['status'] == 'PENDING'
    assert request['resource'] == f'{approval_setup["profile_id"]}/{approval_setup["environment_id"]}'
    assert approval_setup['me']['userId'] in [s['userId'] for s in request['approverStatuses']]


def test_get_profile_permissions(approval_setup):
    permissions = britive.my_approvals.get_profile_permissions(
        profile_id=approval_setup['profile_id'], environment_id=approval_setup['environment_id']
    )
    assert isinstance(permissions, list)


def test_revoke_request(approval_setup, pending_request):
    assert britive.my_approvals.approve_request(request_id=pending_request, comments='pysdktest') is None
    assert _status(approval_setup, pending_request) == 'APPROVED'
    assert britive.my_approvals.revoke_request(request_id=pending_request, comments='pysdktest revoke') is None
    assert _status(approval_setup, pending_request) == 'REVOKED'
    assert britive.my_approvals.get(request_id=pending_request)['revokerComment'] == 'pysdktest revoke'


def test_revoke_requests(approval_setup, pending_request):
    britive.my_approvals.approve_request(request_id=pending_request, comments='pysdktest')
    response = britive.my_approvals.revoke_requests(request_ids=[pending_request], comments='pysdktest bulk revoke')
    assert pending_request in response['success']
    assert response['failed'] == {}
    assert _status(approval_setup, pending_request) == 'REVOKED'


@pytest.mark.skip(reason='approver groups are only on Access Builder requests')
def test_get_approver_group():
    pass
