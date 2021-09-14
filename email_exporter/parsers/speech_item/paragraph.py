from .speech_item_abc import SpeechItemABC


class Paragraph(SpeechItemABC):
    def __init__(self, text):
        self._text = text

    def add_to_speech(self, speech):
        speech.p(self._text)
        return super().add_to_speech(speech)
