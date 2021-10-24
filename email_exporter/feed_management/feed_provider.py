from .feed import Feed


class FeedProvider:

    def __init__(self, config, firestore_client, storage_provider, logger):
        self.collection = config.get("FEED_COLLECTION")
        self.db = firestore_client
        self.storage_provider = storage_provider
        self._logger = logger
        self._feed_cache = {}

    def get_feed(self, key):
        self._logger.info(f"Getting feed for key: {key}")
        if key in self._feed_cache:
            self._logger.info(f"Key {key} found in feed cache. Using cached feed")
            return self._feed_cache[key]
        else:
            self._logger.info(f"Key {key} not found in feed cache. Feching feed")
            feed = self._get_feed(key)
            if feed is not None:
                self._feed_cache[key] = feed
            return feed

    def _get_feed(self, key):
        doc = self.db.collection(self.collection).document(key).get()
        if not doc.exists:
            # TODO: Signup process to create feed
            raise KeyError(f"Feed not found for key: {key}")

        data = doc.to_dict()

        return Feed.from_dict(key, data, self.storage_provider)

    def push_feed(self, feed):
        self.db.collection(self.collection).document(feed.key).set(
            feed.to_dict()
        )

    def apply_feeds(self, prune=True):
        self._logger.info(f"Applying {len(self._feed_cache)} feeds")

        applied_feeds = set()
        for key, feed in self._feed_cache.items():
            try:
                if prune:
                    feed.prune()
                self.push_feed(feed)
                feed.update_rss()
                applied_feeds.add(key)
            except Exception:
                self._logger.exception(f"While applying feed [{key}] an error occured")

        for key in applied_feeds:
            self._feed_cache.pop(key)

        self._logger.info(f"Feeds applied: {len(applied_feeds)} feeds updated")

    def __del__(self):
        if len(self._feed_cache) > 0:
            self._logger.error(
                f"Feeds not flushed. Dropping {len(self._feed_cache)} feeds")
