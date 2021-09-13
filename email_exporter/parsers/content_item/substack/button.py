from ..content_item_abc import ContentItemABC
from ..util import is_only_link
import re


class Button(ContentItemABC):

    def get_ssml(self):
        return super().get_ssml()

    def get_description(self):
        return super().get_description()

    @staticmethod
    def match_component(component):
        if len(component.find_all("a", class_=re.compile(r"button$"))) != 0:
            return True

        if component.name == "div" and "class" in component.attrs and\
                any(class_.endswith("subscribe-widget") for class_ in component["class"]):
            return True

        if component.name == "p" and len(component.contents) == 1 and\
                component.contents[0].name == "a" and len(component.a.find_all("span")) == 1 and\
                is_only_link(component):
            return True

        return False
