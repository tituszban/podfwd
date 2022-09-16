from typing import Optional
from ..shared import Dependencies
from firebase_admin import firestore
from ..feed_management import Feed, FeedProvider
from ..cloud import StorageProvider, TextToSpeech

import uuid


def clone_collection(collection_from_name, collection_to_name):
    deps = Dependencies.default()
    firestore_client = deps.get(firestore.Client)

    collection_from = firestore_client.collection(collection_from_name)
    collection_to = firestore_client.collection(collection_to_name)

    for document in collection_from.get():
        collection_to.document(document.id).set(
            document.to_dict()
        )

    return "Success: Clone"


def create_feed(
        deps: Dependencies, key: str, bucket_name: str,
        item_lifetime_days: int = 7, logging_bucket: Optional[str] = "autopodcast-logs"):
    storage_provider = deps.get(StorageProvider)

    bucket = storage_provider.create_bucket(bucket_name, public=True, logging_bucket=logging_bucket)

    return Feed(key, [], bucket_name, bucket, item_lifetime_days)


def create_creator_feed(email, start_item={}, voice=""):
    deps = Dependencies.default()
    feed_provider = deps.get(FeedProvider)

    try:
        feed_provider.get_feed(email)
        raise Exception(f"Feed with key {email} already exists")
    except KeyError:
        pass

    bucket_name = f"creator-{str(uuid.uuid4()).split('-')[-1]}"

    feed = create_feed(deps, email, bucket_name)

    if start_item:
        pass    # TODO
    # TODO: set voice

    feed.update_rss()
    feed_provider.push_feed(feed)


def create_example_creator_feed():
    email = "example@creator.com"
    create_creator_feed(email)


def test_feed_alias():
    deps = Dependencies.default()

    feed_provider = deps.get(FeedProvider)

    feed_provider.get_feed("tituszban")


def add_feed_alias():
    deps = Dependencies.default()

    feed_provider = deps.get(FeedProvider)

    feed_provider.add_feed_alias("SYhLtwlSg98XUBhaPUtB", "tituszban")


def pronounce():
    text = """
<speak>
    <phoneme alphabet=\"x-samba\" ph=\"gergeI\">Gergely</phoneme>
    <phoneme alphabet=\"x-samba\" ph=\"Or\\:\\os\">Orosz</phoneme>
</speak>
    """

    deps = Dependencies.default()

    t2s = deps.get(TextToSpeech)

    sound_bytes = t2s.t2s(text)

    with open("sample.mp3", "wb") as f:
        f.write(sound_bytes)
