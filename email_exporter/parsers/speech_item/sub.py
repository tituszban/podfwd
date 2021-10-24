from .speech_item_abc import SpeechItemABC


class Sub(SpeechItemABC):
    def __init__(self, text, alias):
        self._text = text
        self._alias = alias

    def add_to_speech(self, speech):
        speech.sub(value=self._text, alias=self._alias)
        return super().add_to_speech(speech)

    def __repr__(self):
        return f"speech_item.{type(self).__name__}({self._text}, {self._alias})"