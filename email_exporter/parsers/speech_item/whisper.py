from .speech_item_abc import SpeechItemABC

class Whisper(SpeechItemABC):
    def __init__(self, text):
        self._text = text

    def add_to_speech(self, speech):
        speech.whisper(self._text)
        return super().add_to_speech(speech)