from .banner import Banner
from .firewall import Firewall
from .itsm import Itsm
from .notification_mediums import NotificationMediums


class GlobalSettings:
    def __init__(self, britive) -> None:
        self.banner = Banner(britive)
        self.firewall = Firewall(britive)
        self.notification_mediums = NotificationMediums(britive)
        self.itsm = Itsm(britive)
