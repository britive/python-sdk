import base64
import datetime
import hashlib
import hmac
import json
import os
from .. import exceptions


class FederationProvider:
    def __init__(self):
        pass

    def get_token(self):
        raise NotImplemented()


class AzureSystemAssignedManagedIdentityFederationProvider(FederationProvider):
    def __init__(self, audience: str = None):
        self.audience = audience if audience else 'https://management.azure.com/'
        super().__init__()

    def get_token(self):
        # azure-identity is not a hard requirement of this SDK but is required for the
        # azure provider so checking to ensure it exists
        try:
            from azure.identity._exceptions import CredentialUnavailableError
        except ImportError:
            raise Exception('azure-identity required - please install azure-identity package to use the azure managed '
                            'identity federation provider')

        try:
            from azure.identity import ManagedIdentityCredential
            token = ManagedIdentityCredential().get_token(self.audience).token
            return f'OIDC::{token}'
        except ImportError:
            raise Exception('azure-identity required - please install azure-identity package to use the azure managed '
                            'identity federation provider')
        except CredentialUnavailableError:
            msg = 'the codebase is not executing in a azure environment or some other issue is causing the ' \
                  'managed identity credentials to be unavailable'
            raise exceptions.NotExecutingInAzureEnvironment(msg)


class AzureUserAssignedManagedIdentityFederationProvider(FederationProvider):
    def __init__(self, client_id: str, audience: str = None):
        self.audience = audience if audience else 'https://management.azure.com/'
        self.client_id = client_id
        super().__init__()

    def get_token(self):
        # azure-identity is not a hard requirement of this SDK but is required for the
        # azure provider so checking to ensure it exists
        try:
            from azure.identity._exceptions import CredentialUnavailableError
        except ImportError:
            raise Exception('azure-identity required - please install azure-identity package to use the azure managed '
                            'identity federation provider')

        try:
            from azure.identity import ManagedIdentityCredential
            token = ManagedIdentityCredential(client_id=self.client_id).get_token(self.audience).token
            return f'OIDC::{token}'
        except ImportError:
            raise Exception('azure-identity required - please install azure-identity package to use the azure managed '
                            'identity federation provider')
        except CredentialUnavailableError:
            msg = 'the codebase is not executing in a azure environment or some other issue is causing the ' \
                  'managed identity credentials to be unavailable'
            raise exceptions.NotExecutingInAzureEnvironment(msg)


class GithubFederationProvider(FederationProvider):
    def __init__(self, audience: str = None):
        self.audience = audience
        super().__init__()

    def get_token(self):
        import requests
        url = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_URL')
        bearer_token = os.environ.get('ACTIONS_ID_TOKEN_REQUEST_TOKEN')

        if not url or not bearer_token:
            msg = 'the codebase is not executing in a github environment and/or the action is ' \
                  'is not set to use oidc permissions'
            raise exceptions.NotExecutingInGithubEnvironment(msg)

        headers = {
            'User-Agent': 'actions/oidc-client',
            'Authorization': f'Bearer {bearer_token}'
        }

        if self.audience:
            url += f'&audience={self.audience}'

        response = requests.get(url, headers=headers)
        return f'OIDC::{response.json()["value"]}'


class AwsFederationProvider(FederationProvider):
    def __init__(self, profile: str, tenant: str, duration: int = 900):
        from ..britive import Britive  # doing import here to avoid circular dependency
        self.profile = profile
        self.duration = duration
        temp_tenant = tenant
        if not temp_tenant:
            self.tenant = os.getenv('BRITIVE_TENANT')
        if not temp_tenant:
            print('Error: the aws federation provider requires the britive tenant as part of the signing algorithm')
            raise exceptions.TenantMissingError()
        self.tenant = Britive.parse_tenant(temp_tenant).split(':')[0]  # remove the port if it exists
        super().__init__()

    @staticmethod
    def sign(key, msg):
        return hmac.new(key, msg.encode("utf-8"), hashlib.sha256).digest()

    @staticmethod
    def get_signature_key(key, date_stamp, region_name, service_name):
        k_date = AwsFederationProvider.sign(('AWS4' + key).encode('utf-8'), date_stamp)
        k_region = AwsFederationProvider.sign(k_date, region_name)
        k_service = AwsFederationProvider.sign(k_region, service_name)
        k_signing = AwsFederationProvider.sign(k_service, 'aws4_request')
        return k_signing

    def get_token(self):
        # boto3 is not a hard requirement of this SDK but is required for the
        # aws provider so checking to ensure it exists
        try:
            import boto3
            import botocore.exceptions as botoexceptions
        except ImportError:
            raise Exception('boto3 required - please install boto3 package to use the aws federation provider')

        # and do all the complex logic for sigv4 signing the sts get-caller-identity endpoint
        session = None
        try:
            session = boto3.Session(profile_name=self.profile)
        except botoexceptions.ProfileNotFound as e:
            raise Exception(f'Error: {str(e)}')

        creds = session.get_credentials()
        access_key_id = creds.access_key
        secret_access_key = creds.secret_key
        session_token = creds.token

        # set some defaults
        service = 'sts'
        region = session.region_name or 'us-east-1'  # default to us-east-1 if no region available
        endpoint = f'https://sts.{region}.amazonaws.com/'
        request_body = 'Action=GetCallerIdentity&Version=2011-06-15'
        t = datetime.datetime.utcnow()
        date_stamp = t.strftime('%Y%m%d')  # Date w/o time, used in credential scope

        # these are all possible headers for 1) canonical/signed 2) actual request
        headers = {
            'host': {
                'value': f'sts.{region}.amazonaws.com',
                'include_in_request': False,  # britive backend will auto-add host header when calling sts endpoint
            },
            'x-amz-date': {
                'value': t.strftime('%Y%m%dT%H%M%SZ'),
                'include_in_request': True
            },
            'x-britive-workload-aws-tenant': {
                'value': self.tenant,
                'include_in_request': True
            },
            'x-britive-expires': {
                'value': f'{(t + datetime.timedelta(seconds=self.duration)).strftime("%Y%m%dT%H%M%SZ")}',
                'include_in_request': True
            }
        }

        # we only want to include the session token if we are dealing with temporary credentials
        # otherwise the sigv4 signing method does not need this value (which would be None)
        if session_token:
            headers['x-amz-security-token'] = {
                'value': session_token,
                'include_in_request': True
            }

        # ************* TASK 1: CREATE A CANONICAL REQUEST *************
        # http://docs.aws.amazon.com/general/latest/gr/sigv4-create-canonical-request.html

        # Step 1: Create the canonical headers. Header names must be trimmed and lowercase, and sorted in code point
        # order from low to high. Note that there is a trailing \n.
        canonical_header_parts = sorted([f'{h.strip().lower()}:{v["value"]}' for h, v in headers.items()])
        canonical_headers = '\n'.join(canonical_header_parts) + '\n'

        # Step 2: Create the list of signed headers. This lists the headers in the canonical_headers list,
        # delimited with ";" and in alpha order. Note: The request can include any headers; canonical_headers and
        # signed_headers include those that you want to be included in the hash of the request.
        signed_headers = ';'.join(sorted([h.strip().lower() for h, v in headers.items()]))

        # Step 3: Create payload hash. In this example, the payload (body of the request) contains the request parameters.
        payload_hash = hashlib.sha256(request_body.encode('utf-8')).hexdigest()

        # Step 4: Combine elements to create canonical request
        canonical_request_components = [
            'POST',  # method
            '/',  # canonical_uri
            '',  # canonical_querystring
            canonical_headers,
            signed_headers,
            payload_hash
        ]
        canonical_request = '\n'.join(canonical_request_components)

        # ************* TASK 2: CREATE THE STRING TO SIGN*************
        # Match the algorithm to the hashing algorithm you use, either SHA-1 or SHA-256 (recommended)
        algorithm = 'AWS4-HMAC-SHA256'
        credential_scope_components = [
            date_stamp,
            region,
            service,
            'aws4_request'
        ]
        credential_scope = '/'.join(credential_scope_components)
        string_components_to_sign = [
            algorithm,
            headers['x-amz-date']['value'],
            credential_scope,
            hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()
        ]
        string_to_sign = '\n'.join(string_components_to_sign)

        # ************* TASK 3: CALCULATE THE SIGNATURE *************
        # Create the signing key using the function defined above.
        signing_key = self.get_signature_key(secret_access_key, date_stamp, region, service)

        # Sign the string_to_sign using the signing_key
        signature = hmac.new(signing_key, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

        # ************* TASK 4: ADD SIGNING INFORMATION TO THE REQUEST *************
        # Put the signature information in a header named Authorization.
        authorization_header_parts = [
            algorithm,
            f'Credential={access_key_id}'
        ]
        authorization_header = f'{algorithm} Credential={access_key_id}/{credential_scope}, ' \
                               f'SignedHeaders={signed_headers}, Signature={signature}'

        # Except for the authorization header, the headers must be included in the canonical_headers and
        # signed_headers values, as noted earlier. order here is not significant.
        # Python note: The 'host' header is added automatically by the Python 'requests' library.
        request_headers = {h: v['value'] for h, v in headers.items() if v['include_in_request'] and v['value']}
        request_headers['authorization'] = authorization_header

        token = {
            'iam_request_url': endpoint,
            'iam_request_body': request_body,
            'iam_request_headers': request_headers
        }

        token_encoded = base64.urlsafe_b64encode(json.dumps(token).encode('utf-8'))
        return f'AWS::{token_encoded.decode("utf-8")}'


class BitbucketFederationProvider(FederationProvider):
    def __init__(self):
        super().__init__()

    # https://support.atlassian.com/bitbucket-cloud/docs/integrate-pipelines-with-resource-servers-using-oidc/
    def get_token(self):
        id_token = os.environ.get('BITBUCKET_STEP_OIDC_TOKEN')
        if not id_token:
            msg = 'the codebase is not executing in a bitbucket environment and/or the `oidc` flag ' \
                  'is not set on the pipeline step'
            raise exceptions.NotExecutingInBitbucketEnvironment(msg)
        return f'OIDC::{id_token}'
