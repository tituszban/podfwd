from ..content_item_abc import ContentItemABC
from ssml import tags
from ... import description_item
import re


class Tweet(ContentItemABC):

    def get_ssml(self):  # TODO: Improve this
        return [
            tags.PText(self._get_text_content())
        ]

    def get_description(self):
        return [
            description_item.Embed(self._component)
        ]

    @staticmethod
    def match_component(component):
        if len(component.find_all("blockquote", class_=re.compile("twitter-tweet$"))) != 0:
            return True

        return False
