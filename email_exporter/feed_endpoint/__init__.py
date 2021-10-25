from ..shared import Dependencies
from ..feed_management import FeedProvider

deps = Dependencies.default()


def get_feed_rss(feed_name):
    feed_provider = deps.get(FeedProvider)
    feed = feed_provider.get_feed(feed_name)
    return feed.to_rss()
