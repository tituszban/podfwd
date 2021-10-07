from .speech_item_abc import SpeechItemABC


class Text(SpeechItemABC):
    def __init__(self, text):
        self._text = text

    def add_to_speech(self, speech):
        speech.add_text(self._text)
        return super().add_to_speech(speech)

    def __repr__(self):
        return f"speech_item.{type(self).__name__}({self._text})"
