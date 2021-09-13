from ..content_item_abc import ContentItemABC

class CaptionedImage(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        # Directly received
        if "class" in component.attrs and "captioned-image-container-static" in component["class"]:
            return True

        try:
            if component.name == "div" and \
                    len(component.find_all("table")) == 1 and \
                    len(component.table.find_all("td")) == 3 and \
                    len(component.table.find_all("img")) == 1:
                # Image fingerprint: Forwarded, gmail sanitised
                return True
        except AttributeError:
            return False

        return False
