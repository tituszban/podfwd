from .item_emitter import ItemEmitter
from .content_item import ContentItem
import re


class SubstackItemEmitter(ItemEmitter):
    def get_items(self, inbox_item):
        post_components = inbox_item.soup.find_all("div", class_=re.compile(r"post$"))
        # TODO: Handle preamble.
        # Check if markup$ is better than post$
        item_count = 0
        for post_component in post_components:
            if post_component.div is None:
                continue
            for component in post_component.div.children:
                item_count += 1
                yield ContentItem.to_item(component)
        
        if item_count > 0:
            return

        post_components = inbox_item.soup.find_all(
            "div", 
            style=re.compile(r"font-size:\s?16px;.*line-height:\s?26px"))

        for post_component in post_components:
            if post_component.div is None:
                continue
            for component in post_component.div.children:
                item_count += 1
                yield ContentItem.to_item(component)
