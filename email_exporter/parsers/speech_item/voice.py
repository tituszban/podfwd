from .speech_item_abc import SpeechItemABC


class Voice(SpeechItemABC):
    def __init__(self, text, voice):
        self._text = text
        self._voice = voice

    def add_to_speech(self, speech):
        speech.voice(value=self._text, name=self._voice)
        return super().add_to_speech(speech)

    def __repr__(self):
        return f"speech_item.{type(self).__name__}({self._text}, {self._voice})"
