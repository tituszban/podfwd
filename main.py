import os
from email_parser import process_inbox
from t2s import TextToSpeech
from storage import StorageProvider
import datetime
from feed_management import FeedProvider, Feed, Item


def find_max_id(item):
    return max([i["idx"] for i in item] + [0])


def old_items(items, lifetime_days=7):
    now = datetime.datetime.now()
    for item in items:
        date = datetime.datetime.strptime(
            item["date"], "%a, %d %b %Y %H:%M:%S %z").replace(tzinfo=None)
        age = now - date
        print(age)
        if age > datetime.timedelta(days=lifetime_days):
            yield item


def main(request):
    feed_file_name = "feed.xml"
    sa_json = os.environ.get("SA_FILE", None)
    if json:
        t2s = TextToSpeech(json=json)
        storage = StorageProvider(json=sa_json)
        feed_provider = FeedProvider(json=sa_json)
    else:
        t2s = TextToSpeech()
        storage = StorageProvider()
        feed_provider = FeedProvider("autopodcast")

    def update_feed(email, items):
        feed = feed_provider.get_feed(email)

        if feed.bucket_name == "":
            feed_provider.push_feed(feed)
            print(
                f"No bucket name for {feed.email}. Some data just got dropped"
            )
            return

        bucket = storage.get_bucket(feed.bucket_name)

        next_id = feed.next_id
        for i, item in enumerate(items):
            idx = next_id + i
            url = bucket.upload_bytes(f"{idx}.mp3", item["sound_data"])

            feed.items.append(Item(
                item["title"],
                "",
                item["date"],
                url,
                idx
            ))

        feed_provider.push_feed(feed)

        current_feed = bucket.download_xml(feed_file_name)
        updated_feed = feed.to_rss(current_feed)
        bucket.upload_xml(feed_file_name, updated_feed)

    items_by_sender = {}
    for sender, item in process_inbox():
        item["sound_data"] = t2s.lines_to_speech(item["content"])
        items_by_sender[sender] = items_by_sender.get(sender, []) + [item]

    for sender, items in items_by_sender.items():
        update_feed(sender, items)

    return "Success"


# if __name__ == "__main__":
#     main(None)
#     # blob_test()
