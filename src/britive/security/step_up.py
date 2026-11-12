class StepUpAuth:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/step-up/authenticate/TOTP'

    def authenticate(self, otp: str, headers: dict = None) -> dict:
        """Authenticate a TOTP challenge, forwarding optional headers such as `X-On-Behalf-Of`."""
        data = {'otp': otp}
        return self.britive.post(self.base_url, json=data, headers=headers)
