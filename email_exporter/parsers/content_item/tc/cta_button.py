from ..content_item_abc import ContentItemABC
from ..util import is_only_link


class CtaButton(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        contents_without_nl = [content for content in component.contents if content != "\n"]
        if component.name == "p" and len(contents_without_nl) == 1 and\
                contents_without_nl[0].name == "a" and\
                "read more" in component.text.lower() and \
                is_only_link(component):
            return True

        return False
