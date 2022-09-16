from logging import Logger

from email_exporter.inbox import InboxItem
from email_exporter.parsers.parser_abc import ParserABC
from .tc_parser import TcItemEmitter
from .substack_parser import SubstackItemEmitter
from .general_parser import GeneralParser
from .emitter_parser import EmitterParser


class ParserSelector:
    def __init__(self, logger: Logger):
        self._logger = logger
        self.emitters_by_domain = {
            "techcrunch.com": TcItemEmitter,
            "substack.com": SubstackItemEmitter
        }

    def get_parser(self, content_item: InboxItem) -> ParserABC:
        return self._get_parser(content_item.sender)

    def _get_parser(self, sender: str) -> ParserABC:
        self._logger.info(f"Selecting parser for {sender}")

        sender_domain = sender.split("@")[-1]

        if sender_domain in self.emitters_by_domain:
            self._logger.info(
                f"Found emitter parser for {sender} ({sender_domain}): {self.emitters_by_domain[sender_domain]}")
            return EmitterParser(self._logger, self.emitters_by_domain[sender_domain]())

        self._logger.info(f"No parser found for {sender} ({sender_domain}): General parser is used")
        return GeneralParser(self._logger)
