from .text_item import TextItem
from .tweet_item import TweetItem
from .util import is_tweet


class ContentItem:
    @staticmethod
    def to_item(component):
        if is_tweet(component):
            return TweetItem(component)
        return TextItem(component)

