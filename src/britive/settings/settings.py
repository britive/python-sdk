from .banner import SettingsBanner


# this class is just a logical grouping construct


class Settings:
    def __init__(self, britive):
        self.britive = britive
        self.banner = SettingsBanner(britive)

