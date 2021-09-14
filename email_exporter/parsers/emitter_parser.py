from .parser_abc import ParserABC
from functools import reduce


class EmitterParser(ParserABC):
    def __init__(self, logger, emitter):
        self._logger = logger
        self._emitter = emitter

    def parse(self, inbox_item):
        assert inbox_item.soup is not None, "Soup not provided"

        items = list(self._emitter.get_items(inbox_item))

        audio_items = reduce(lambda arr, item: [*arr, *item.get_ssml()], items, [])

        return [], []
