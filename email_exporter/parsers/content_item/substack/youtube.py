from ..content_item_abc import ContentItemABC
import requests
from ssml import tags
from ... import description_item


class Youtube(ContentItemABC):

    def _get_youtube_video_info(self, video_id):
        res = requests.get("https://www.youtube.com/oembed", params={
            "url": f"https://www.youtube.com/watch?v={video_id}",
            "format": "json"
        })
        return res.json()

    def get_ssml(self):
        try:
            video_id = self._component.img["src"].split("/")[-1]
            info = self._get_youtube_video_info(video_id)

            return [
                tags.PText(f"YouTube video {info['title']} by {info['author_name']}.")
            ]

        except:     # noqa: E722
            return []

    def get_description(self):
        return [
            description_item.Embed(self._component)
        ]

    @staticmethod
    def match_component(component):
        if component.name == "a" and "class" in component.attrs and\
                any(class_.endswith("youtube-wrap") for class_ in component["class"]):
            return True

        return False
