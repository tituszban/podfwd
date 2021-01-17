from .util import get_text_content, is_only_link, get_link_texts

class TextItem:
    def __init__(self, component):
        self.component = component
        self.name = component.name
        self.text = get_text_content(component)
        self.is_only_link = is_only_link(component)
        self.links = get_link_texts(component)