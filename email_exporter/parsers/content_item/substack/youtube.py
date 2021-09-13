from ..content_item_abc import ContentItemABC


class Youtube(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        if component.name == "a" and "class" in component.attrs and any(class_.endswith("youtube-wrap") for class_ in component["class"]):
            return True

        return False
