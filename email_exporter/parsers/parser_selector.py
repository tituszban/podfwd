from .parser_abc import ParserABC
from .tc_parser import TcParser


class ParserSelector:
    def __init__(self, logger):
        self.logger = logger
        self.parsers_by_domain = {
            "techcrunch.com": TcParser
        }

    def get_parser(self, sender):
        sender_domain = sender.split("@")[-1]
        if sender_domain in self.parsers_by_domain:
            return self.parsers_by_domain[sender_domain](self.logger)
        return ParserABC(self.logger)   # TODO: Create best effor default parser
