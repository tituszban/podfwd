from logging import Logger
from typing import Type

from email_exporter.inbox import InboxItem
from email_exporter.parsers.parser_abc import ParserABC
from .tc_parser import TcItemEmitter
from .substack_parser import SubstackItemEmitter
from .mailgun_parser import MailgunItemEmitter
from .ghost_parser import GhostItemEmitter
from .general_parser import GeneralParser
from .emitter_parser import EmitterParser
from .item_emitter import ItemEmitter


class ParserSelector:
    def __init__(self, logger: Logger):
        self._logger = logger
        self.emitters_by_domain: dict[str, Type[ItemEmitter]] = {
            "techcrunch.com": TcItemEmitter,
            "substack.com": SubstackItemEmitter,
            "cautiousoptimism.news": MailgunItemEmitter,
            "platformer.news": GhostItemEmitter,
        }

    def get_parser(self, content_item: InboxItem) -> ParserABC:
        return self._get_parser(content_item.sender)

    def _get_parser(self, sender: str) -> ParserABC:
        self._logger.info(f"Selecting parser for {sender}")

        sender_domain = sender.split("@")[-1].rstrip(">")

        if sender_domain in self.emitters_by_domain:
            self._logger.info(
                f"Found emitter parser for {sender} ({sender_domain}): {self.emitters_by_domain[sender_domain]}")
            return EmitterParser(self._logger, self.emitters_by_domain[sender_domain]())

        self._logger.info(f"No parser found for {sender} ({sender_domain}): General parser is used")
        return GeneralParser(self._logger)
