from abc import ABC, abstractmethod


class SpeechItemABC(ABC):
    @abstractmethod
    def add_to_speech(self, speech):
        return speech
