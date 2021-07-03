import secrets
from .feed import Feed

class FeedProvider:

    def __init__(self, config, firestore_client, storage_provider):
        self.collection = config.get("FEED_COLLECTION")


        self.db = firestore_client
        self.storage_provider = storage_provider

    def get_feed(self, email):
        doc = self.db.collection(self.collection).document(email).get()
        if not doc.exists:
            # TODO: Signup process to create feed
            return None

        data = doc.to_dict()

        return Feed.from_dict(email, data, self.storage_provider)

    def push_feed(self, feed):
        self.db.collection(self.collection).document(feed.email).set(
            feed.to_dict()
        )
