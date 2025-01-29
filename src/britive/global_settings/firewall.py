class Firewall:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/settings/firewall'

    def list_rules(self) -> list:
        """
        Get the firewall rules.

        :returns: List of the firewall rules.
        """

        return self.britive.get(self.base_url)

    def save_rules(self, rules: list, default_action: str = 'DENY', antilockout: bool = False) -> dict:
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

    def save_fields(self, fields: dict) -> None:
        """
        Save firewall fields.

        :param fields: Dict of firewall fields.
            Key:
                type: str
                desc: Name of the firewall field, e.g. `country` or `client_ip`.
            Value:
                type: dict
                desc: key: value pairs containing requisite values for [`header`, `field_type`, `info`, `operators`]
                header:
                    type: str
                    desc: The rules are executed as per the priority number
                field_type:
                    type: str
                    desc: `ip` or `string`.
                info:
                    type: str
                    desc: Information about, or description of, the field.
                operators:
                    type: str
                    desc: Options: `EQUALS`|`CONTAINS`|`STARTSWITH`|`ENDSWITH`
        :returns: Details of the saved firewall fields.
        """

        return self.britive.post(f'{self.base_url}/fields', json={'fields': fields})

    def list_fields(self) -> list:
        """
        Get the firewall fields.

        :returns: List of the firewall fields.
        """

        return self.britive.get(f'{self.base_url}/fields')
