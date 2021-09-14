from .speech_item_abc import SpeechItemABC

class Audio(SpeechItemABC):
    def __init__(self, source):
        self._source = source

    def add_to_speech(self, speech):
        speech.audio(self._source)
        return super().add_to_speech(speech)