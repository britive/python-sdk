from .banner import Banner
from .notification_mediums import NotificationMediums


class GlobalSettings:
    def __init__(self, britive) -> None:
        self.banner = Banner(britive)
        self.notification_mediums = NotificationMediums(britive)
