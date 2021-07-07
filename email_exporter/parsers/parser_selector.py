from .parser_abc import ParserABC
from .tc_parser import TcParser
from .substack_parser import SubstackParser
from .general_parser import GeneralParser


class ParserSelector:
    def __init__(self, logger):
        self.logger = logger
        self.parsers_by_domain = {
            "techcrunch.com": TcParser,
            "substack.com": SubstackParser
        }

    def get_parser(self, content_item):
        return self._get_parser(content_item.sender)

    def _get_parser(self, sender):
        sender_domain = sender.split("@")[-1]
        if sender_domain in self.parsers_by_domain:
            return self.parsers_by_domain[sender_domain](self.logger)
        return GeneralParser(self.logger)
