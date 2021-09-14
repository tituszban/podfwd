from ..content_item_abc import ContentItemABC
from ... import speech_item


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
            speech_item.Pause(self.pause_duration.get(self._component.name, "750ms")),
            speech_item.Paragraph(self._get_text_content())
        ]

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        return component.name in ["h1", "h2", "h3", "h4", "h5", "h6"]
