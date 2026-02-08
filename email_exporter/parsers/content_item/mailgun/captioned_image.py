from ..content_item_abc import ContentItemABC
from ... import description_item


class CaptionedImage(ContentItemABC):
    """
    Matches captioned images in mailgun emails.
    These are typically tables with class "img-container" containing an image and caption.
    """

    def get_ssml(self):
        # Images don't produce speech
        return []

    def get_description(self):
        result = []
        if img := self._component.find("img"):
            result.append(description_item.Image(img))
        if caption := self._component.find("p", class_="img-caption"):
            result.append(description_item.Text(caption))
        return result

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match table elements with class "img-container"
        if component.name == "table" and "class" in component.attrs:
            if "img-container" in component["class"]:
                return True

        return False
