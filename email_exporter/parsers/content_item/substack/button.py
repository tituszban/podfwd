from ..generic import NullContentItem
from ..util import is_only_link
import re


class Button(NullContentItem):

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
