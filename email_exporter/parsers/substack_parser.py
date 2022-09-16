from .item_emitter import ItemEmitter
from .content_item import ContentItem
import re


class SubstackItemEmitter(ItemEmitter):
    def get_items(self, inbox_item):
        post_components = inbox_item.soup.find_all("div", class_=re.compile(r"post$"))
        # TODO: Handle preamble.
        # Check if markup$ is better than post$

        for post_component in post_components:
            for component in post_component.div.children:
                yield ContentItem.to_item(component)
