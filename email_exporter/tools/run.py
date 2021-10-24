from ..shared import Dependencies
from firebase_admin import firestore
from ..feed_management import Feed, FeedProvider
from ..cloud import StorageProvider

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


def create_feed(deps, key, bucket_name, item_lifetime_days=7):
    storage_provider = deps.get(StorageProvider)

    bucket = storage_provider.create_bucket(bucket_name, public=True)

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
