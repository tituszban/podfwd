from abc import ABC, abstractmethod
from email.message import Message
from typing import Iterator, Tuple


class InboxABC(ABC):

    @abstractmethod
    def get_messages(self, search_criteria: str = 'UNFLAGGED') -> Iterator[Tuple[int, Message]]:
        raise NotImplementedError()

    @abstractmethod
    def discard_message(self, idx: int) -> None:
        raise NotImplementedError()

    @property
    @abstractmethod
    def email_address(self) -> str:
        raise NotImplementedError()
