from ..content_item_abc import ContentItemABC
from ... import description_item


class ImageCard(ContentItemABC):
    """
    Matches image card divs in Ghost emails.
    These are div elements with class "kg-image-card" containing images
    and optional captions.
    
    Example structure:
    <div class="kg-card kg-image-card">
        <img src="..." class="kg-image" alt="..." />
    </div>
    
    Or with a caption:
    <div class="kg-card kg-image-card kg-card-hascaption">
        <img src="..." />
        <figcaption class="kg-card-figcaption">Caption text</figcaption>
    </div>
    """

    def get_ssml(self):
        # Images don't produce speech, but we could read alt text if desired
        return []

    def get_description(self):
        result = []
        
        # Get the image
        if img := self._component.find("img"):
            result.append(description_item.Image(img))
        
        # Get caption if present (figcaption element)
        if caption := self._component.find("figcaption"):
            caption_text = caption.get_text(strip=True)
            if caption_text:
                result.append(description_item.Text(f"<p>{caption_text}</p>"))
        
        return result

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        # Match div elements with class "kg-image-card"
        if component.name == "div" and "class" in component.attrs:
            if "kg-image-card" in component["class"]:
                return True

        return False
