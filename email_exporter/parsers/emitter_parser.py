from .parser_abc import ParserABC
from functools import reduce
from ssml_builder.core import Speech


class EmitterParser(ParserABC):
    def __init__(self, logger, emitter):
        self._logger = logger
        self._emitter = emitter
        self.speech_limit = 5000

    def _speech_items_to_ssml(self, speech_items):
        def convert(_speech_items):
            speech = Speech()
            for item in _speech_items:
                item.add_to_speech(speech)
            return speech.speak()

        i = 0
        while i < len(speech_items):
            j = i
            while len(convert(speech_items[i:j])) <= self.speech_limit and j <= len(speech_items):
                j += 1
            if i == j:
                raise Exception("speech item is too long")
            yield convert(speech_items[i:j-1])
            i = j

    def parse(self, inbox_item):
        assert inbox_item.soup is not None, "Soup not provided"

        items = list(self._emitter.get_items(inbox_item))

        speech_items = reduce(lambda arr, item: [*arr, *item.get_ssml()], items, [])

        ssml = list(self._speech_items_to_ssml(speech_items))

        return ssml, []
