from ..content_item_abc import ContentItemABC
from ..util import is_only_link
import re

"""
<p style="text-align: left; color: #333; font-size: 19px; font-weight: bold; line-height: 26px; margin: 35px 0 15px;">
 <a href="https://link.techcrunch.com/click/25016890.55889/aHR0cHM6Ly90ZWNoY3J1bmNoLmNvbS8yMDIxLzA3LzE1L2Fubm91bmNpbmctdGhlLWFnZW5kYS1mb3ItdGhlLWRpc3J1cHQtc3RhZ2UtdGhpcy1zZXB0ZW1iZXIvP3V0bV9tZWRpdW09VENuZXdzbGV0dGVyJnRwY2M9VENzdGFydHVwc25ld3NsZXR0ZXImdXRtX2NhbXBhaWduPVRDc3RhcnR1cHN3ZWVrbHk/5efa60b389f523479b4459bbDcc740be2" style="background: #14c435; color: white; padding: 12px 18px; text-decoration: none" target="_blank">
  Read More
 </a>
</p>
"""


class CtaButton(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        contents_without_nl = [content for content in component.contents if content != "\n"]
        if component.name == "p" and len(contents_without_nl) == 1 and\
                contents_without_nl[0].name == "a" and\
                "read more" in component.text.lower() and \
                is_only_link(component):
            return True

        return False
