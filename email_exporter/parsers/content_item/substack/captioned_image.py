from ..content_item_abc import ContentItemABC
from ... import description_item


class CaptionedImage(ContentItemABC):

    def get_ssml(self):
        return []

    def get_description(self):
        return [
            description_item.Image(self._component.find("img")),
            description_item.Image(f"<p>{self._get_text_content()}</p>")
        ]

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False
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
