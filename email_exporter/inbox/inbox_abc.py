from abc import ABC, abstractmethod


class InboxABC(ABC):

    @abstractmethod
    def get_messages(self):
        raise NotImplementedError()

    @abstractmethod
    def discard_message(self, idx):
        raise NotImplementedError()

    @property
    @abstractmethod
    def email_address(self):
        raise NotImplementedError()
