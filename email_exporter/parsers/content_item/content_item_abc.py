from abc import ABC, abstractmethod
from .util import get_text_content


class ContentItemABC(ABC):

    def __init__(self, component, to_item):
        self._component = component
        self._to_item = to_item

    @abstractmethod
    def get_ssml(self):
        return []
        # raise NotImplementedError()

    @abstractmethod
    def get_description(self):
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def match_component(component):
        raise NotImplementedError()

    def _get_text_content(self):
        return get_text_content(self._component)
