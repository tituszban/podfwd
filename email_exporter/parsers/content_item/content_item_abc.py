from abc import ABC, abstractmethod


class ContentItemABC(ABC):

    def __init__(self, component):
        self._component = component

    @abstractmethod
    def get_ssml(self):
        raise NotImplementedError()

    @abstractmethod
    def get_description(self):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def match_component(component):
        raise NotImplementedError()
