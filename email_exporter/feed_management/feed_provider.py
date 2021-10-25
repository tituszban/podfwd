from email_exporter.config import Config
from email_exporter.cloud import StorageProvider
from firebase_admin.firestore import Client as FirestoreClient
from logging import Logger
from .feed import Feed


class FeedProvider:

    def __init__(
            self,
            config: Config,
            firestore_client: FirestoreClient,
            storage_provider: StorageProvider,
            logger: Logger) -> None:
        self.collection = config.get("FEED_COLLECTION")
        self.db = firestore_client
        self.storage_provider = storage_provider
        self._logger = logger
        self._feed_cache = {}

    def get_feed(self, key: str) -> Feed:
        self._logger.info(f"Getting feed for key: {key}")
        if key in self._feed_cache:
            self._logger.info(f"Key {key} found in feed cache. Using cached feed")
            return self._feed_cache[key]
        else:
            self._logger.info(f"Key {key} not found in feed cache. Feching feed")
            feed, keys = self._get_feed(key)
            if feed is not None:
                for c_key in keys:
                    self._feed_cache[c_key] = feed
            return feed

    def _get_feed_doc(self, key):
        ref = self.db.collection(self.collection).document(key)
        snapshot = ref.get()
        if not snapshot.exists:
            # TODO: Signup process to create feed
            raise KeyError(f"Feed not found for key: {key}")

        data = snapshot.to_dict()

        keys = [key]

        while "alias" in data:
            ref = data["alias"]
            snapshot = ref.get()
            if not snapshot.exists:
                raise KeyError(f"Feed not found for key: {key}; Invalid alias for {keys[-1]}")
            key = snapshot.id
            data = snapshot.to_dict()
            self._logger.info(f"Redirected feed {keys[-1]} to {key} via alias")
            keys.append(key)

        return ref, key, data, keys

    def _get_feed_info(self, key: str):
        _, key, data, keys = self._get_feed_doc(key)
        return key, data, keys

    def _get_feed_ref(self, key: str):
        ref, _, _, _ = self._get_feed_doc(key)
        return ref

    def _get_feed(self, key):
        key, data, keys = self._get_feed_info(key)

        return Feed.from_dict(key, data, self.storage_provider), keys

    def push_feed(self, feed):
        self.db.collection(self.collection).document(feed.key).set(
            feed.to_dict()
        )

    def add_feed_alias(self, key: str, alias_key: str):
        ref = self._get_feed_ref(key)

        current_alias = self.db.collection(self.collection).document(alias_key).get()
        if current_alias.exists:
            raise KeyError(f"Cannot create alias {alias_key}; A document with the key already exists")
        
        self.db.collection(self.collection).document(alias_key).set({
            "alias": ref
        })

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
