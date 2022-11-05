class Approvals():
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/v1/approvals/'

    def review(self, decision : bool, approval_id : str) -> dict:
        """for internal use"""
        params = {}
        if decision:
            params['approveRequest' ] = 'yes'
        else:
            params['approveRequest' ] = 'no'
        return self.britive.patch(f'{self.base_url}{approval_id}', params=params)

    def approve(self, approval_id: str) -> dict:
        return self.review(True, approval_id)

    def reject(self, approval_id: str) -> dict:
        return self.review(False, approval_id)

    def get(self, approval_id: str) -> dict:
        return self.britive.get(f'{self.base_url}/{approval_id}')

    def list(self, filter : str = None, requestType : str = None):
        params = {
            'requestType' : requestType,
            'filter' : filter
        }
        return self.britive.get(self.base_url, params=params)
