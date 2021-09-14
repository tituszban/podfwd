from .null_content_item import NullContentItem


class EmptyParagraph(NullContentItem):

    @staticmethod
    def match_component(component):
        return component.name == "p" and component.text.strip() == ""
