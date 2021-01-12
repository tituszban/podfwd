import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import secrets
import rss_gen


class Item:
    def __init__(self, title, description, date, url, idx):
        self.title = title
        self.description = description
        self.url = url
        self.idx = idx
        self.date = date

    @staticmethod
    def from_dict(d):
        return Item(
            d["title"],
            d["description"],
            d["date"],
            d["url"],
            d["id"]
        )

    def to_dict(self):
        return {
            "title": self.title,
            "description": self.description,
            "url": self.url,
            "id": self.idx,
            "date": self.date
        }


class Feed:
    def __init__(self, email, items, bucket_name):
        self.email = email
        self.items = items
        self.bucket_name = bucket_name

    @staticmethod
    def from_dict(email, d):
        return Feed(
            email,
            list(map(Item.from_dict, d["items"])),
            d["bucket_name"]
        )

    def to_dict(self):
        return {
            "items": [item.to_dict() for item in self.items],
            "bucket_name": self.bucket_name
        }

    def to_rss(self, feed):
        root, _ = rss_gen.read(feed)
        return rss_gen.write(
            root,
            [
                (item.title, item.description, item.url, item.idx, item.date)
                for item in self.items
            ]
        )

    @property
    def next_id(self):
        if len(self.items) <= 0:
            return 0
        return max([item.idx for item in self.items]) + 1


class FeedProvider:
    collection = "feeds"

    def __init__(self, projectId="autopodcast", json=None):
        if json:
            cred = credentials.Certificate(json)
            firebase_admin.initialize_app(cred)
        elif firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
            cred = credentials.ApplicationDefault()
            firebase_admin.initialize_app(cred, options={
                'projectId': projectId,
            })

        self.db = db = firestore.client()

    def get_feed(self, email):
        doc = self.db.collection(self.collection).document(email).get()
        if not doc.exists:
            # TODO: bucket_name = secrets.token_hex(8)
            return Feed(email, [], "")

        data = doc.to_dict()

        return Feed.from_dict(email, data)

    def push_feed(self, feed):
        self.db.collection(self.collection).document(feed.email).set(
            feed.to_dict()
        )
