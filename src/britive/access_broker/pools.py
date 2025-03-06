class Pools:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/resource-manager/remote-broker/pools'

    def create(self, name: str, description: str = '', keep_alive: int = 60, disconnect: int = 86400) -> dict:
        """
        Create a new broker pool.

        :param name: Name of the new broker pool.
        :param description: Description of the new broker pool. Default: ''
        :param keep_alive: Keep Alive Seconds of the new broker pool. Default: 60, Minimum: 60, Maximum: 1200
        :param disconnect: Disconnect Seconds of the new broker pool. Default: 86400
        :return: Details of the new broker pool.
        """

        params = {
            'name': name,
            'description': description,
            'keep-alive-seconds': keep_alive,
            'disconnect-seconds': disconnect,
        }

        return self.britive.post(self.base_url, json=params)

    def get(self, pool_id: str) -> dict:
        """
        Retrieve broker pool by ID.

        :param pool_id: Broker pool ID.
        :return: Details of the broker pool.
        """

        return self.britive.get(f'{self.base_url}/{pool_id}')

    def list(self, name_filter: str = '') -> list:
        """
        List broker pools with ability to filter by name.

        :param name_filter: Filter broker pools by starts with.
        :return: List of broker pools.
        """

        params = {
            'name': name_filter,
        }

        return self.britive.get(self.base_url, params=params)['data']

    def list_brokers(self, pool_id: str) -> list:
        """
        Retrieve brokers for the broker pool.

        :param pool_id: Broker pool ID.
        :return: List of brokers for the broker pool.
        """

        return self.britive.get(f'{self.base_url}/{pool_id}/brokers')

    def list_resources(self, pool_id: str, search_text: str = '') -> list:
        """
        Retrieve resources for the broker pool.

        :param pool_id: Broker pool ID.
        :param search_text: Filter resources by search text.
        :return: List of resources for the broker pool.
        """

        params = {'filter': f'brokerPool eq {pool_id}', 'searchText': search_text}

        return self.britive.get(f'{self.britive.base_url}/resource-manager/resources', params=params)

    def update(
        self, pool_id: str, name: str = None, description: str = None, keep_alive: int = None, disconnect: int = None
    ) -> dict:
        """
        Update broker pool by ID.

        :param pool_id: Broker pool ID.
        :param name: Updated name of the broker pool.
        :param description: Updated description of the broker pool.
        :param keep_alive: Updated Keep Alive Seconds of the broker pool.
        :param disconnect: Updated Disconnect Seconds of the broker pool.
        :return: Details of the updated broker pool.
        """

        params = self.get(pool_id=pool_id)

        if name:
            params['name'] = name
        if description:
            params['description'] = description
        if keep_alive:
            params['keep-alive-seconds'] = keep_alive
        if disconnect:
            params['disconnect-seconds'] = disconnect

        return self.britive.put(f'{self.base_url}/{params.pop("pool-id", pool_id)}', json=params)

    def delete(self, pool_id: str) -> None:
        """
        Delete a broker pool by ID - this operation deletes all tokens, labels, and resource associations with the pool.

        :param pool_id: Broker pool ID.
        :return: None.
        """

        return self.britive.delete(f'{self.base_url}/{pool_id}')

    def create_token(self, pool_id, name: str, description: str = '') -> dict:
        """
        Create new token for the broker pool - newly created tokens have an `INACTIVE` status.

        :param pool_id: Broker pool ID.
        :param name: Name of the new token.
        :param description: Description of the token. Default: ''
        :return: Details of the new token.
        """

        params = {'token-name': name, 'description': description}

        return self.britive.post(f'{self.base_url}/{pool_id}/tokens', json=params)

    def list_tokens(self, pool_id: str) -> list:
        """
        Retrieve authentication tokens for the broker pool.

        :param pool_id: Broker pool ID.
        :return: List of authentication tokens.
        """

        return self.britive.get(f'{self.base_url}/{pool_id}/tokens')

    def update_token(self, pool_id: str, name: str, description: str = None, status: str = None) -> dict:
        """
        Update a token by name.

        :param pool_id: Broker pool ID.
        :param name: Name of the token to update.
        :param description: Updated description of the token.
        :param status: Updated status of the token. Options: [ACTIVE, INACTIVE]
        :return: Details of the updated token.
        """

        params = {}

        if description:
            params['description'] = description
        if status:
            params['status'] = status.upper()

        return self.britive.patch(f'{self.base_url}/{pool_id}/tokens/{name}', json=params)

    def delete_token(self, pool_id: str, name: str) -> None:
        """
        Delete a token by name.

        :param pool_id: Broker pool ID.
        :param name: Name of the token.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{pool_id}/tokens/{name}')

    def add_label(self, pool_id: str, key: str, values: list) -> dict:
        """
        Add a resource label to the broker pool.

        :param pool_id: Broker pool ID.
        :param key: The key of the resource label.
        :param values: The list of desired values of the resource label.
        :return: Details of the added resource label.
        """

        params = {'key': key, 'label-values': values}

        return self.britive.post(f'{self.base_url}/{pool_id}/labels/', json=params)

    def list_labels(self, pool_id: str) -> list:
        """
        Retrieve resource labels for the broker pool.

        :param pool_id: Broker pool ID.
        :return: List of resource labels for the broker pool.
        """

        return self.britive.get(f'{self.base_url}/{pool_id}/labels')

    def update_label(self, pool_id: str, key: str, values: list) -> dict:
        """
        Add a resource label to the broker pool.

        :param pool_id: Broker pool ID.
        :param key: The key of the resource label.
        :param values: The list of desired values of the resource label.
        :return: Details of the updated resource label.
        """

        params = {'label-values': values}

        return self.britive.post(f'{self.base_url}/{pool_id}/labels/{key}', json=params)

    def delete_label(self, pool_id: str, key: str) -> None:
        """
        Remove a resource label from the broker pool.

        :param pool_id: Broker pool ID.
        :param key: The key of the resource label.
        :return: None
        """

        return self.britive.delete(f'{self.base_url}/{pool_id}/labels/{key}')
