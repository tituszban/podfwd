from ..content_item_abc import ContentItemABC
import re
from ssml import tags
from ... import description_item


class Author(ContentItemABC):

    def get_ssml(self):
        return [
            tags.PText(self._get_text_content()),
            tags.Break(time="500ms")
        ]

    def get_description(self):
        return [
            description_item.Util(f"<p>{self._get_text_content()}</p>")
        ]

    @staticmethod
    def match_component(component):
        if not hasattr(component, "attrs"):
            return False

        if "class" in component.attrs and "meta-author-wrap" in component["class"]:    # Directly received
            return True
        try:
            if component.name == "table" and \
                    len(
                        component.tbody.tr.find_all("td", recursive=False)[-1]
                        .div.find_all("td", class_=re.compile(r"post-meta-item$"))
                    ) > 0:
                # Author fingerprint: Forwarded, gmail sanitised
                return True
        except AttributeError:
            return False

        return False
