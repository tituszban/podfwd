from .speech_item_abc import SpeechItemABC


class Prosody(SpeechItemABC):
    def __init__(self, text, rate, pitch, volume):
        self._text = text
        self._rate = rate
        self._pitch = pitch
        self._volume = volume

    def add_to_speech(self, speech):
        speech.prosody(value=self._text, rate=self._rate, pitch=self._pitch, volume=self._volume)
        return super().add_to_speech(speech)

    def __repr__(self):
        return f"speech_item.{type(self).__name__}({self._text}, {self._rate}, {self._pitch}, {self._volume})"
