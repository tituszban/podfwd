from ..generic import NullContentItem


class HorizontalRule(NullContentItem):

    @staticmethod
    def match_component(component):
        return len(component.contents) == 1 and component.contents[0].name == "hr"
