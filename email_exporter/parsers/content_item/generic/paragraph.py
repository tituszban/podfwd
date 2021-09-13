from ..content_item_abc import ContentItemABC


class Paragraph(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return component.name == "p"
