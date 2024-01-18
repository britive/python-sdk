from datetime import datetime


class SettingsBanner:
    def __init__(self, britive):
        self.britive = britive
        self.base_url = f'{self.britive.base_url}/settings/banner'

    def get(self) -> dict:
        """
        Get the banner configuration.

        :returns: Details of the banner.
        """
        return self.britive.get(self.base_url)
    
    def set(self, display_banner: bool, message: str, message_type: str, start_datetime: datetime = None,
            end_datetime: datetime = None, time_zone: str = None) -> dict:
        """
        Sets the banner.

        :param display_banner: Whether to display the banner.
        :param message: The banner message.
        :param message_type: The banner type. This will drive the styling. Valid values are `INFO`,
            `WARNING`, and `CAUTION`.
        :param start_datetime: Optional start date and time for when the banner should be displayed.
            No timezone information should be encoded. If provided, must also provide `end_datetime` and `timezone`.
        :param end_datetime: Optional end date and time for when the banner should be displayed.
            No timezone information should be encoded. If provided, must also provide `start_datetime` and `timezone`.
        :param time_zone: Optional ISO timezone under which `start_datetime` and `end_datetime` should be interpreted.
            If provided, must also provide `start_datetime` and `end_datetime`.
        :returns: Details of the banner.
        """

        data = {
            'status': 'ON' if display_banner else 'OFF',
            'message': message,
            'messageType': message_type
        }

        schedule_fields = [start_datetime, end_datetime, time_zone]
        all_schedule_fields_present = all(v is not None for v in schedule_fields)
        no_schedule_fields_present = all(v is None for v in schedule_fields)

        if not all_schedule_fields_present and not no_schedule_fields_present:
            raise ValueError('if providing schedule information then start_datetime, '
                             'end_datetime, and time_zone are required')

        if all_schedule_fields_present:
            data['messageSchedule'] = {
                'endDate': end_datetime.isoformat(sep=' ', timespec='seconds'),
                'startDate': start_datetime.isoformat(sep=' ', timespec='seconds'),
                'timeZone': time_zone
            }

        return self.britive.post(self.base_url, json=data)
