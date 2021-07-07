from abc import ABC


class ParserABC(ABC):
    def __init__(self, *args, **kwargs):
        pass

    def parse(self, content_item):
        return [], []
