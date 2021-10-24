from .tc_parser import TcParser, TcItemEmitter
from .substack_parser import SubstackParser, SubstackItemEmitter
from .general_parser import GeneralParser
from .emitter_parser import EmitterParser


class ParserSelector:
    def __init__(self, logger):
        self._logger = logger
        self.emitters_by_domain = {
            "techcrunch.com": TcItemEmitter,
            "substack.com": SubstackItemEmitter
        }
        self.parsers_by_domain = {
            "techcrunch.com": TcParser,
            "substack.com": SubstackParser
        }

    def get_parser(self, content_item):
        return self._get_parser(content_item.sender)

    def _get_parser(self, sender):
        self._logger.info(f"Selecting parser for {sender}")
        sender_domain = sender.split("@")[-1]

        if sender_domain in self.emitters_by_domain:
            self._logger.info(
                f"Found emitter parser for {sender} ({sender_domain}): {self.emitters_by_domain[sender_domain]}")
            return EmitterParser(self._logger, self.emitters_by_domain[sender_domain]())

        if sender_domain in self.parsers_by_domain:
            self._logger.info(
                f"Found domain parser for {sender} ({sender_domain}): {self.parsers_by_domain[sender_domain]}")
            return self.parsers_by_domain[sender_domain](self._logger)

        self._logger.info(f"No parser found for {sender} ({sender_domain}): General parser is used")
        return GeneralParser(self._logger)
