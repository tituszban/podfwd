from . import rss_gen
from .item import Item, FileInfo
import datetime
import os


DEFAULT_FEED_FILE_NAME = "feed.xml"


class Logo:
    def __init__(
        self,
        url="https://storage.googleapis.com/autopodcast/autopod_logo.png",
        size=(144, 144),
        **_
    ):
        self.url = url
        self.size = size

    @staticmethod
    def from_dict(d):
        return Logo(**d)

    def to_dict(self):
        return {
            "url": self.url,
            "size": self.size
        }


class Branding:
    def __init__(
        self,
        title="PODFWD",
        author="PODFWD",
        link="https://podfwd.com",
        email="autopod.tb@gmail.com",
        keywords=("PODFWD",),
        subtitle="Automated podcasts, t2s news letters",
        summary="Automated podcasts, t2s news letters",
        categories=[
            "News:Tech News",
            "News:Daily News",
            "Technology"
        ],
        logo=Logo()
    ):
        self.title = title
        self.author = author
        self.link = link
        self.email = email
        self.keywords = keywords
        self.subtitle = subtitle
        self.summary = summary
        self.categories = categories
        self.logo = logo

    @staticmethod
    def from_dict(d):
        return Branding(**{
            **d,
            "logo": Logo.from_dict(d.get("logo", {}))
        })

    def to_dict(self):
        return {
            "title": self.title,
            "author": self.author,
            "link": self.link,
            "email": self.email,
            "keywords": self.keywords,
            "subtitle": self.subtitle,
            "summary": self.summary,
            "categories": self.categories,
            "logo": self.logo.to_dict()
        }


class Feed:
    def __init__(
        self,
        key,
        items,
        bucket_name,
        bucket,
        item_lifetime_days,
        block=True,
        branding=Branding(),
        feed_file_name=DEFAULT_FEED_FILE_NAME,
        **_
    ):
        self.key = key
        self.items = items
        self.bucket_name = bucket_name
        self.bucket = bucket
        self.item_lifetime_days = item_lifetime_days
        self.block = block
        self.branding = branding
        self.feed_file_name = feed_file_name

    @staticmethod
    def from_dict(email, data, storage_provider):
        return Feed(
            key=email,
            items=list(map(Item.from_dict, data.get("items", []))),
            bucket_name=data["bucket_name"],
            bucket=storage_provider.get_bucket(data["bucket_name"]),
            item_lifetime_days=data.get("item_lifetime_days", 7),
            branding=Branding.from_dict(data.get("branding", {})),
            feed_file_name=data.get("feed_file_name", DEFAULT_FEED_FILE_NAME)
        )

    def to_dict(self):
        return {
            "items": [item.to_dict() for item in self.items],
            "bucket_name": self.bucket_name,
            "item_lifetime_days": self.item_lifetime_days,
            "block": self.block,
            "branding": self.branding.to_dict(),
            "feed_file_name": self.feed_file_name
        }

    def add_item_bytes(self, title, description, date, sender, data):
        idx = self.next_id
        now = datetime.datetime.now()

        file_name = Item.filename_from_id(idx)
        url = self.bucket.upload_bytes(file_name, data)
        file_info = FileInfo(url=url, file_name=file_name)

        item = Item(title=title, description=description, date=date, idx=idx,
                    sender=sender, file_info=file_info, created_date=now)
        self.items.append(item)
        return item

    def add_item_url(self, title, description, date, sender, url):
        idx = self.next_id
        now = datetime.datetime.now()

        file_info = FileInfo(url, is_external=True)

        item = Item(title=title, description=description, date=date, idx=idx,
                    sender=sender, file_info=file_info, created_date=now)
        self.items.append(item)
        return item

    def add_item_file_path(self, title, description, date, sender, file_path):
        idx = self.next_id
        now = datetime.datetime.now()

        file_name = os.path.basename(file_path)
        url = self.bucket.upload_from_file_path(file_name, file_path)
        file_info = FileInfo(url, file_name)

        item = Item(title=title, description=description, date=date, idx=idx,
                    sender=sender, file_info=file_info, created_date=now)
        self.items.append(item)
        return item

    def to_rss(self):
        return rss_gen.generate_feed(self)

    def update_rss(self):
        if self.bucket is None:
            return
        updated_feed = self.to_rss()
        self.bucket.upload_xml(self.feed_file_name, updated_feed)

    @property
    def next_id(self):
        if len(self.items) <= 0:
            return 0
        return max([item.idx for item in self.items]) + 1

    def prune(self):
        old_items = set()
        now = datetime.datetime.now()
        for item in self.items:
            if item.file_info.is_removed or item.file_info.is_external:
                continue
            date = item.try_get_date().replace(tzinfo=None)
            age = now - date
            if age.days >= self.item_lifetime_days:
                old_items.add(item)

        for item in old_items:
            self.bucket.delete_blob(item.file_info.file_name)
            item.file_info.is_removed = True
