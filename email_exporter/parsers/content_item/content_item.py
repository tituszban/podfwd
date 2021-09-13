from email_exporter.parsers.content_item.tc.content_image import ContentImage
from .text_item import TextItem
from .tweet_item import TweetItem
from .string_item import StringItem
from .util import is_tweet


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
                return content_item(component)
        raise RuntimeError(f"No content item was matched to component: {component}")

    class Special:
        @staticmethod
        def to_tc_header(component, content_item):
            return tc.Header(component, content_item)

        # if type(component) == str:
        #     return StringItem(component)
        # if is_tweet(component):
        #     return TweetItem(component)
        # return TextItem(component)
