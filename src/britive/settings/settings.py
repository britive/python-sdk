from .banner import SettingsBanner

# this class is just a logical grouping construct


class Settings:
    def __init__(self, britive) -> None:
        self.britive = britive
        self.banner = SettingsBanner(britive)

