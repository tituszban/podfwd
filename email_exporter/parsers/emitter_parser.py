from .parser_abc import ParserABC
from functools import reduce
from ssml_builder.core import Speech
import bs4
from collections import defaultdict


class EmitterParser(ParserABC):
    def __init__(self, logger, emitter):
        self._logger = logger
        self._emitter = emitter
        self.speech_limit = 5000
        self.description_limit = 4000

    def _speech_items_to_ssml(self, content_items):
        speech_items = reduce(lambda arr, item: [*arr, *item.get_ssml()], content_items, [])

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

    def _content_items_to_description(self, content_items):
        description_items = []

        for i, item in enumerate(content_items):
            for d in item.get_description():
                description_items.append((d, i))

        def remove_attrs(component, attrs_to_keep=("alt", "src", "href")):
            for attr in [attr for attr in component.attrs if attr not in attrs_to_keep]:
                del component[attr]

        attrs = set({})

        def transform():
            for item, i in description_items:
                if isinstance(item, bs4.element.PageElement):

                    for attr in item.attrs:
                        attrs.add(attr)

                    children = [item, *item.findChildren(recursive=True)]
                    for child in children:
                        remove_attrs(child)
                    yield str(item), i
                if isinstance(item, str):
                    yield item, i

        annotated_descriptions = list(transform())

        description = list(map(lambda d: d[0], annotated_descriptions))

        annotation = defaultdict(int)

        for desc, i in annotated_descriptions:
            annotation[i] += len(desc)
        
        return description, annotation

    def _get_description(self, content_items, inbox_item):
        _content_items = list(content_items)

        title = f"<h1>{inbox_item.title}</h1>"

        while len(_content_items) > 0:
            descriptions, annotation = self._content_items_to_description(_content_items)

            description = [title, *descriptions]

            if len('\n'.join(description)) <= self.description_limit:
                return description
            
            len_by_content_type = reduce(lambda d, i: {**d, i.content_type: 0}, _content_items, {})

            for i, l in annotation.items():
                len_by_content_type[_content_items[i].content_type] += l

            content_type_to_remove = max(len_by_content_type, key=lambda k: len_by_content_type[k])

            _content_items = [item for item in _content_items if item.content_type != content_type_to_remove]

        return [title]

    def parse(self, inbox_item):
        assert inbox_item.soup is not None, "Soup not provided"

        items = list(self._emitter.get_items(inbox_item))

        ssml = list(self._speech_items_to_ssml(items))

        description = self._get_description(items, inbox_item)

        return ssml, description
