from email_exporter.inbox import InboxItem
from ssml import SsmlTagABC
from .content_item import ContentItemABC
from .item_emitter import ItemEmitter
from .parser_abc import ParserABC
from functools import reduce
from ssml import SpeechBuilder
from .parsed_item import ParsedItem


class EmitterParser(ParserABC):
    def __init__(self, logger, emitter: ItemEmitter):
        self._logger = logger
        self._emitter = emitter
        self.speech_limit = 5000
        self.description_limit = 400000

    def _content_items_to_ssml(self, content_items: list[ContentItemABC]):
        ssml_tags: list[SsmlTagABC] = reduce(
            lambda arr, item: [*arr, *item.get_ssml()], content_items, [])

        def convert(_ssml_tags: list[SsmlTagABC]):
            speech = SpeechBuilder()
            for item in _ssml_tags:
                speech.add_tag(item)
            return speech.speak()

        i = 0
        while i < len(ssml_tags):
            j = i
            while len(convert(ssml_tags[i:j])) <= self.speech_limit and j <= len(ssml_tags):
                j += 1
            if i == j:
                raise Exception("speech item is too long")
            yield convert(ssml_tags[i:j - 1])
            i = j - 1

    def _content_items_to_description(self, content_items: list[ContentItemABC], content_type_to_remove: set[str]):
        return [
            description
            for item in content_items
            for description in item.get_description()
            if description.content_type not in content_type_to_remove
        ]

    def _get_description(self, content_items, inbox_item):

        title = f"<h1>{inbox_item.title}</h1>"

        remove_href = False
        content_type_to_remove = set()

        while len(descriptions := self._content_items_to_description(content_items, content_type_to_remove)) > 0:
            desc_text = [d.to_text(remove_href) for d in descriptions]

            if len('\n'.join([title, *desc_text])) <= self.description_limit:
                return desc_text

            remove_href = not remove_href

            if remove_href:
                continue

            len_by_content_type = reduce(lambda d, i: {**d, i.content_type: 0}, descriptions, {})

            for desc, text in zip(descriptions, desc_text):
                len_by_content_type[desc.content_type] += len(text)

            next_content_type_to_remove = max(len_by_content_type, key=lambda k: len_by_content_type[k])

            content_type_to_remove.add(next_content_type_to_remove)

        return [title]

    def parse(self, inbox_item: InboxItem):
        assert inbox_item.soup is not None, "Soup not provided"

        self._logger.info(f"Getting items for {inbox_item}")

        items = list(self._emitter.get_items(inbox_item))

        self._logger.info(f"Created {len(items)} content items")

        ssml = list(self._content_items_to_ssml(items))

        self._logger.info(f"Created {len(ssml)} SSML lines; total length: {sum(map(lambda s: len(s), ssml))}")

        description = self._get_description(items, inbox_item)

        self._logger.info(
            f"Created {len(description)} description lines; total length: {sum(map(lambda s: len(s), description))}")

        return ParsedItem(ssml, description)
