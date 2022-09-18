from ..generic import NullContentItem
from ..util import is_only_link


class CtaButton(NullContentItem):

    @staticmethod
    def match_component(component):
        if not hasattr(component, "contents"):
            return False
        contents_without_nl = [content for content in component.contents if content != "\n"]
        if component.name == "p" and len(contents_without_nl) == 1 and\
                contents_without_nl[0].name == "a" and\
                "read more" in component.text.lower() and \
                is_only_link(component):
            return True

        return False
