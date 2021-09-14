from .speech_item_abc import SpeechItemABC

class Pause(SpeechItemABC):
    def __init__(self, time):
        self._time = time

    def add_to_speech(self, speech):
        speech.pause(self._time)
        return super().add_to_speech(speech)