from datetime import datetime, timezone, timedelta
import time
from . import exceptions


class MySecrets:
    """
    This class is meant to be called by end users (as part of custom API integration work or pybritive CLI).
    It is an API layer on top of the actions that can be performed on the "My Secrets" page of the Britive UI.

    No "administrative" access is required by the methods in this class. Each method will only return resources/allow
    actions which are permitted to be performed by the user/service identity, as identified by an API token or
    interactive login bearer token.

    It is entirely possible that an administrator who makes these API calls could get nothing returned, as that
    administrator may not have access to any secrets.
    """

    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/secretmanager'

    def __get_vault_id(self):
        # only 1 vault is allowed per tenant, so we can reliably grab the ID of that vault
        try:
            return self.britive.get(f'{self.base_url}/vault')['id']
        except KeyError as e:
            if 'id' in str(e):
                raise exceptions.NoSecretsVaultFound()

    def list(self, path: str = '/', search: str = None) -> list:
        """
        Recursively list all secrets under the given path.

        Only entries/secrets assigned to the provided identity, via a policy, are listed.

        :param path: Optional argument used to specify where in the hierarchy to begin listing secrets. Include
            leading / if provided.
        :param search: Optional argument used to filter the list of returned secrets by searching on the secret name.
        :return: List of secrets for which the provided identity has access to view.
        """

        params = {
            'recursiveSecrets': True,
            'getmetadata': True,
            'path': path,
            'type': 'secret'
        }

        if search:
            params['filter'] = f"name co '{search}'"

        return self.britive.get(f'{self.base_url}/vault/{self.__get_vault_id()}/secrets', params=params)

    def view(self, path: str, justification: str = None, wait_time: int = 60,
             max_wait_time: int = 600) -> dict:
        """
        Retrieve the decrypted secret value.

        :param path: The path to the secret. Include the leading /.
        :param justification: Optional justification if viewing the secret requires approval.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the secret
            request was approved.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :return: Details of the decrypted secret.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises AccessDenied: if the caller does not have access to the secret being requested.
        :raises ApprovalWorkflowTimedOut: if max_wait_time has been reached while waiting for approval.
        :raises ApprovalWorkflowRejected: if the request to view the secret was rejected.
        :raises InvalidRequest: if the node/secret does not exist
        """

        vault_id = self.__get_vault_id()
        quit_time = datetime.now(timezone.utc) + timedelta(seconds=max_wait_time)
        params = {
            'path': path
        }
        data = {
            'justification': justification
        }
        first = True
        while True:  # this is not loop forever due to exceptions raised or returning the secret value
            try:
                # handle when the time has expired waiting for approval
                if datetime.now(timezone.utc) >= quit_time:
                    raise exceptions.ApprovalWorkflowTimedOut()

                # attempt to get the secret value and return it
                return self.britive.post(
                    f'{self.base_url}/vault/{vault_id}/accesssecrets',
                    params=params,
                    json=data if first else None
                )['value']

            # 403 will be returned when approval is required or pending or access is denied
            except exceptions.ForbiddenRequest as e:
                if 'PE-0011' in str(e) and not justification:
                    if first:
                        raise exceptions.ApprovalRequiredButNoJustificationProvided() from e
                    else:
                        raise exceptions.ApprovalWorkflowRejected() from e
                if 'PE-0002' in str(e):
                    raise exceptions.AccessDenied()
                if 'PE-0010' in str(e):  # approval to view the secret is pending...
                    first = False
                    time.sleep(wait_time)
                else:
                    raise e

    def download(self, path: str, justification: str = None, wait_time: int = 60, max_wait_time: int = 600) -> dict:
        """
        Retrieve the decrypted secret file.

        It is left to the caller of this method to persist the file contents to disk. Example of usage is below.

        r = b.my_secrets.download(path='/examplefile')
        with open(r['filename'], 'wb') as f:
            f.write(r['content_bytes'])

        :param path: The path to the secret. Include the leading /.
        :param justification: Optional justification if viewing the secret requires approval.
        :param wait_time: The number of seconds to sleep/wait between polling to check if the secret
            request was approved.
        :param max_wait_time: The maximum number of seconds to wait for an approval before throwing
            an exception.
        :return: Dict containing the filename of the downloaded file and the content of the file as bytes.
        :raises ApprovalRequiredButNoJustificationProvided: if approval is required but no justification is provided.
        :raises AccessDenied: if the caller does not have access to the secret being requested.
        :raises ApprovalWorkflowTimedOut: if max_wait_time has been reached while waiting for approval.
        """

        vault_id = self.__get_vault_id()
        quit_time = datetime.now(timezone.utc) + timedelta(seconds=max_wait_time)
        params = {
            'path': path
        }

        try:
            # attempt to get the secret file and return it

            return self.britive.get(
                f'{self.base_url}/vault/{vault_id}/downloadfile',
                params=params
            )
        # 403 will be returned when approval is required or access is denied
        except exceptions.ForbiddenRequest as e:
            if 'PE-0011' in str(e):  # justification is required which means we have an approval workflow to deal with
                # lets call view so we can go through the full approval process
                self.view(
                    path=path,
                    justification=justification,
                    wait_time=wait_time,
                    max_wait_time=max_wait_time
                )

                # and then we can get the file again
                return self.britive.get(
                    f'{self.base_url}/vault/{vault_id}/downloadfile',
                    params=params
                )
            if 'PE-0002' in str(e):
                raise exceptions.AccessDenied()
            else:
                raise e
