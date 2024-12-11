from .custom_attributes import CustomAttributes
from .methods import HelperMethods


class Helpers:
    def __init__(self, britive) -> None:
        self.custom_attributes = CustomAttributes(britive)
        self.helper_methods = HelperMethods(britive)
