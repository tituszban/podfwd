from abc import ABC, abstractmethod

from ssml_builder import SpeechBuilder


class SpeechItemABC(ABC):
    @abstractmethod
    def add_to_speech(self, speech: SpeechBuilder):
        return speech
