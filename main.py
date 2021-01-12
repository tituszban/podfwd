import os
from email_parser import process_inbox
from t2s import TextToSpeech
from storage import StorageProvider
import datetime
from feed_management import FeedProvider, Feed, Item
from parsers import TcParser
from config import Config


def main(request):
    config = Config()\
        .add_env_variables("AP_")
    
    feed_file_name = "feed.xml"
    sa_json = os.environ.get("SA_FILE", None)
    t2s = TextToSpeech(config)
    storage = StorageProvider(config)
    feed_provider = FeedProvider(config)

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
        parser = TcParser()
        item["content"] = list(parser.parse(item["soup"]))
        item["sound_data"] = t2s.lines_to_speech(item["content"])
        items_by_sender[sender] = items_by_sender.get(sender, []) + [item]

    for sender, items in items_by_sender.items():
        update_feed(sender, items)

    return "Success"


if __name__ == "__main__":
    main(None)
    # blob_test()
