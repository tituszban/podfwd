from abc import ABC, abstractmethod
from typing import Iterable

from ..description_item import DescriptionItemABC
from ..speech_item import SpeechItemABC
from .util import get_text_content
from bs4.element import PageElement


class ContentItemABC(ABC):

    def __init__(self, component, to_item):
        self._component = component
        self._to_item = to_item

    @abstractmethod
    def get_ssml(self) -> Iterable[SpeechItemABC]:
        raise NotImplementedError()

    @abstractmethod
    def get_description(self) -> Iterable[DescriptionItemABC]:
        raise NotImplementedError()

    @staticmethod
    @abstractmethod
    def match_component(component: PageElement) -> bool:
        raise NotImplementedError()

    def _get_text_content(self):
        return get_text_content(self._component)

    def _get_repr_name(self):
        module_path = type(self).__module__.split(".")
        if "content_item" not in module_path:
            return f"{'.'.join(module_path[:-1])}.{type(self).__name__}"

        return f"{'.'.join(module_path[module_path.index('content_item'):-1])}.{type(self).__name__}"

    def __repr__(self):
        return f"{self._get_repr_name()}({self._get_text_content()})"
