import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import secrets
from .feed import Feed

class FeedProvider:

    def __init__(self, config, storage_provider):
        self.collection = config.get("FEED_COLLECTION")

        json = config.get("SA_FILE")
        project_id = config.get("PROJECT_ID")

        if json:
            cred = credentials.Certificate(json)
            firebase_admin.initialize_app(cred)
        elif firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, options={
                'projectId': project_id,
            })

        self.db = firestore.client()
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
