class Firewall:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/settings/firewall'

    def save(self, rules: list, default_action: str = 'DENY', antilockout: bool = False) -> dict:
        """
        Save firewall rules.

        :param rules: List of firewall rules.
            Rule parameters:
                priority:
                    type: int
                    desc: Required - The rules are executed as per the priority number
                action:
                    type: str
                    desc: Required - `ALLOW` or `DENY`.
                field:
                    type: str
                    desc: Required - `country` or `client_ip`
                invert:
                    type: bool
                    desc: `True` of `False` - Default: `False`
                operator:
                    type: str
                    desc: Required - Depends on field - Options: `EQUALS`|`CONTAINS`|`STARTSWITH`|`ENDSWITH`
                values:
                    type: list
                    desc: Required - Depends on field - List of client IPs(v4 and/or v6) or country codes.
        :param default_action: `ALLOW` or `DENY` - Default: `DENY`
        :param antilockout:
        :returns: Details of the saved firewall rules.
        """

        data = {
            'rules': rules,
            'default_action': default_action,
            'antilockout': antilockout,
        }

        return self.britive.post(self.base_url, json=data)

    def list(self): ...

    def get(self): ...

    def updated(self): ...

    def delete(self): ...
