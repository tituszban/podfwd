from ..content_item_abc import ContentItemABC


class Tweet(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        if "class" in component.attrs and "tweet" in component["class"]:    # Directly received
            return True

        if any([
                img["alt"].startswith("Twitter avatar for")
                for img in component.find_all("img")
                if "alt" in img.attrs and img["alt"]]):
            return True

        return False
