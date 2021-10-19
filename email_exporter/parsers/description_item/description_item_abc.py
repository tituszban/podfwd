from abc import ABC, abstractmethod
import bs4


class DescriptionItemABC(ABC):
    attrs_to_keep = ("alt", "src", "href")

    def __init__(self, content):
        self._content = content

    def _remove_attrs(self, component, remove_href):
        attrs_to_keep = [attr for attr in self.attrs_to_keep if attr != "href" or not remove_href]
        for attr in [attr for attr in component.attrs if attr not in attrs_to_keep]:
            del component[attr]

    def to_text(self, remove_href=False):   # TODO: this is not great. Replace with building up components, instead of deleting
        if isinstance(self._content, bs4.element.PageElement):
            children = [self._content, *self._content.findChildren(recursive=True)]
            for child in children:
                self._remove_attrs(child, remove_href)
            return str(self._content)
        if isinstance(self._content, str):
            return self._content
        raise RuntimeError(f"Unknown description content: {type(self._content)}")

    @property
    @abstractmethod
    def content_type(self):
        raise NotImplementedError()
