from ..content_item_abc import ContentItemABC
from ssml import tags
from ... import description_item


class Header(ContentItemABC):

    pause_duration = {
        "h1": "750ms",
        "h2": "650ms",
        "h3": "500ms",
        "h4": "450ms",
        "h5": "400ms",
        "h6": "350ms",
    }

    def get_ssml(self):
        return [
            tags.Break(time=self.pause_duration.get(self._component.name, "750ms")),
            tags.PSText(self._get_text_content())
        ]

    def get_description(self):
        return [
            description_item.Text(self._component)
        ]

    @staticmethod
    def match_component(component):
        return component.name in ["h1", "h2", "h3", "h4", "h5", "h6"]
