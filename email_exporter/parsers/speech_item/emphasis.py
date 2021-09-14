from .speech_item_abc import SpeechItemABC

class Emphasis(SpeechItemABC):
    strong = "strong"
    moderate = "moderate"
    none = "none"
    reduced = "reduced"

    def __init__(self, text, level):
        self._text = text
        assert level in [
            Emphasis.strong,
            Emphasis.moderate,
            Emphasis.none,
            Emphasis.reduced,
        ]
        self._level = level

    def add_to_speech(self, speech):
        speech.emphasis(self._text, self._level)
        return super().add_to_speech(speech)