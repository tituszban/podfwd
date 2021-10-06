from ..content_item_abc import ContentItemABC
from ... import speech_item
import re


class Tweet(ContentItemABC):

    def get_ssml(self):  # TODO: Improve this
        return [
            speech_item.Paragraph(self._get_text_content())
        ]

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        if len(component.find_all("blockquote", class_=re.compile("twitter-tweet$"))) != 0:
            return True

        return False
