from ..content_item_abc import ContentItemABC
from ssml import tags


class Blockquote(ContentItemABC):

    def _get_inner_ssml(self):
        for component in self._component.contents:
            if component == "\n":
                continue
            yield from self._to_item(component).get_ssml()

    def get_ssml(self):
        inner_ssml = list(self._get_inner_ssml())

        if len(inner_ssml) <= 0:
            return []

        return [
            tags.P("Quote."),
            *inner_ssml,
            tags.P("End quote.")
        ]

    def get_description(self):
        for component in self._component.contents:
            if component == "\n":
                continue
            yield from self._to_item(component).get_description()

    @staticmethod
    def match_component(component):
        return component.name == "blockquote"
