from ..content_item_abc import ContentItemABC
from ... import speech_item


class Blockquote(ContentItemABC):

    def get_ssml(self):
        yield speech_item.Paragraph("Quote.")

        for component in self._component.contents:
            if component == "\n":
                continue
            yield from self._to_item(component).get_ssml()

        yield speech_item.Paragraph("End quote.")

    def get_description(self):
        for component in self._component.contents:
            if component == "\n":
                continue
            yield from self._to_item(component).get_description()

    @staticmethod
    def match_component(component):
        return component.name == "blockquote"
