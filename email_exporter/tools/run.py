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
    <break time="750ms"></break>
    <p>
        <s>What is Data Engineering? Part 1.</s>
    </p>
    <break time="500ms"></break>
    <p>
        <s>A broad overview of the data engineering field by former Facebook data engineer Benjamin Rogojan. Part 1.</s>
    </p>
    <p>
        <phoneme alphabet="x-sampa" ph="gergeI">Gergely</phoneme>
        <phoneme alphabet="x-sampa" ph="Or\\:\\os">Orosz</phoneme> Sep 13</p>
    <break time="500ms"></break>
    <p>
        👋 Hi, this is <phoneme alphabet="x-sampa" ph="gergeI">Gergely</phoneme> with a free issue
        of the Pragmatic Engineer Newsletter.
        Today we cover Part 1 of \'What is Data Engineering.\' To get a similarly in-depth article every week,
        subscribe here 👇
    </p>
</speak>
    """.replace("    ", "").replace("\n", "")

    deps = Dependencies.default()

    t2s = deps.get(TextToSpeech)

    sound_bytes = t2s.t2s(text, voice="en-GB-Wavenet-B")

    with open("sample.mp3", "wb") as f:
        f.write(sound_bytes)
