from .speech_item_abc import SpeechItemABC

class Language(SpeechItemABC):
    def __init__(self, text, lang):
        self._text = text
        self._lang = lang

    def add_to_speech(self, speech):
        speech.lang(value=self._text, lang=self._lang)
        return super().add_to_speech(speech)