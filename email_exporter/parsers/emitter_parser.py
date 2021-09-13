from .parser_abc import ParserABC


class EmitterParser(ParserABC):
    def __init__(self, logger, emitter):
        self._logger = logger
        self._emitter = emitter

    def parse(self, content_item):
        assert content_item.soup is not None, "Soup not provided"

        items = list(self._emitter.get_items(content_item))

        return [], []
