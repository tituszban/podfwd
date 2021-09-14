from . import generic
from . import substack
from . import tc


class ContentItem:
    content_items = [
        *tc.items,
        *substack.items,
        *generic.items
    ]

    @staticmethod
    def to_item(component):
        for content_item in ContentItem.content_items:
            if content_item.match_component(component):
                return content_item(component, ContentItem.to_item)
        raise RuntimeError(f"No content item was matched to component: {component}")

    class Special:
        @staticmethod
        def to_tc_header(component, inbox_item):
            return tc.Header(component, ContentItem.to_item, inbox_item)
