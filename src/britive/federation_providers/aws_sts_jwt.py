from .federation_provider import FederationProvider


class AwsStsJwtFederationProvider(FederationProvider):
    def __init__(
        self,
        profile: str = None,
        audience: str = None,
        duration_seconds: int = 300,
        signing_algorithm: str = 'ES384',
    ) -> None:
        self.profile = profile
        self.audience = audience or 'britive'
        self.duration_seconds = max(60, min(3600, duration_seconds))
        self.signing_algorithm = signing_algorithm
        super().__init__()

    def get_token(self) -> str:
        try:
            import boto3
            import botocore.exceptions as botoexceptions
        except ImportError as e:
            raise Exception(
                'boto3 required - please install boto3 package to use the aws-sts-jwt federation provider'
            ) from e

        try:
            session = boto3.Session(profile_name=self.profile)
        except botoexceptions.ProfileNotFound as e:
            raise Exception(f'Error: {e!s}') from e

        sts_client = session.client('sts')

        response = sts_client.get_web_identity_token(
            Audience=[self.audience],
            DurationSeconds=self.duration_seconds,
            SigningAlgorithm=self.signing_algorithm,
        )

        return f'OIDC::{response["WebIdentityToken"]}'
