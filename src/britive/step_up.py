class StepUpAuth:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/step-up/authenticate/TOTP'

    def authenticate(self, otp: str) -> dict:
        data = {'otp': otp}
        return self.britive.post(self.base_url, json=data)
