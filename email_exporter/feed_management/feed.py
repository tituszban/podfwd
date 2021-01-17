from . import rss_gen
from .item import Item
import datetime


class Feed:
    def __init__(self, email, items, bucket_name, bucket, item_lifetime_days):
        self.email = email
        self.items = items
        self.bucket_name = bucket_name
        self.bucket = bucket
        self.item_lifetime_days = item_lifetime_days

    @staticmethod
    def from_dict(email, d, storage_provider):
        return Feed(
            email,
            list(map(Item.from_dict, d.get("items", []))),
            d["bucket_name"],
            storage_provider.get_bucket(d["bucket_name"]),
            d.get("item_lifetime_days", 7)
        )

    def add_item(self, **kwargs):
        item = Item(**kwargs)
        self.items.append(item)
        return item

    def to_dict(self):
        return {
            "items": [item.to_dict() for item in self.items],
            "bucket_name": self.bucket_name,
            "item_lifetime_days": self.item_lifetime_days
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

    def update_rss(self, feed_file_name):
        if self.bucket is None:
            return
        current_feed = self.bucket.download_xml(feed_file_name)
        updated_feed = self.to_rss(current_feed)
        self.bucket.upload_xml(feed_file_name, updated_feed)

    @property
    def next_id(self):
        if len(self.items) <= 0:
            return 0
        return max([item.idx for item in self.items]) + 1

    def prune(self):
        old_items = set()
        now = datetime.datetime.now()
        for item in self.items:
            date = item.try_get_date().replace(tzinfo=None)
            age = now - date
            if age.days >= self.item_lifetime_days:
                old_items.add(item)

        for item in old_items:
            self.items.remove(item)
            self.bucket.delete_blob(item.file_name)
