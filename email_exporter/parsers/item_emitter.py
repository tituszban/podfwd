from abc import ABC, abstractmethod

class ItemEmitter(ABC):
    @abstractmethod
    def get_items(self, content_item):
        raise NotImplementedError()