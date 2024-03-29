from mock import Mock, MagicMock, patch
import pytest
from email_exporter.feed_management.feed_provider import FeedProvider


def test_get_feed_returns_from_collection():
    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(feed_name)
    db_document_client.get.assert_called_once()
    db_document.to_dict.assert_called_once()
    assert feed


def test_get_feed_document_doesnt_exist_throws():
    db_document = Mock()
    db_document.exists = False
    db_document.to_dict = MagicMock()
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    with pytest.raises(KeyError):
        _ = sut.get_feed(feed_name)


def test_get_feed_called_again_returns_from_cache():
    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)
    feed2 = sut.get_feed(feed_name)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(feed_name)
    db_document_client.get.assert_called_once()
    db_document.to_dict.assert_called_once()
    assert feed
    assert feed2 == feed


def _create_document(data, exists=True, id=Mock()):
    db_document = Mock()
    db_document.exists = exists
    db_document.to_dict.return_value = data
    db_document.id = id
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_snapshot = Mock()
    db_document_snapshot.id = id
    db_document_snapshot.get.return_value = db_document
    db_document_snapshot.collection.return_value = db_item_collection
    return db_document_snapshot


def test_get_feed_alias_redirects_to_document():
    bucket_name = "bucket_name"
    root_doc = _create_document({"bucket_name": bucket_name}, id="root_doc")
    alias_doc = _create_document({"alias": root_doc}, id="root_doc")

    db_client = Mock()
    db_client.document.return_value = alias_doc
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)

    assert feed.bucket_name == bucket_name
    alias_doc.get.assert_called_once()


def test_get_feed_nested_alias_redirects_to_document():
    bucket_name = "bucket_name"
    root_doc = _create_document({"bucket_name": bucket_name})
    alias1_doc = _create_document({"alias": root_doc})
    alias2_doc = _create_document({"alias": alias1_doc})

    db_client = Mock()
    db_client.document.return_value = alias2_doc
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)

    assert feed.bucket_name == bucket_name
    alias2_doc.get.assert_called_once()


def test_get_feed_nested_alias_all_cached():
    bucket_name = "bucket_name"
    keys = ["root_doc", "alias1_doc", "alias2_doc"]
    root_doc = _create_document({"bucket_name": bucket_name}, id=keys[0])
    alias1_doc = _create_document({"alias": root_doc}, id=keys[1])
    alias2_doc = _create_document({"alias": alias1_doc}, id=keys[2])

    db_client = Mock()
    db_client.document.return_value = alias2_doc
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(keys[2])

    feed1 = sut.get_feed(keys[2])
    feed2 = sut.get_feed(keys[1])
    feed3 = sut.get_feed(keys[0])

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(keys[2])
    alias2_doc.get.assert_called_once()
    assert feed
    assert feed1 == feed
    assert feed2 == feed
    assert feed3 == feed


def test_push_feed_calls_document_set():
    feed_name = "feed_name"
    feed_dict = Mock()
    feed = Mock()
    feed.to_dict.return_value = feed_dict
    feed.key = feed_name
    feed.updated_items = []

    db_document_client = Mock()
    db_document_client.set = MagicMock()
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    sut.push_feed(feed)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(feed_name)
    db_document_client.set.assert_called_once_with(feed_dict)


def test_push_feed_calls_collection_set_for_updated_items():
    item_id = 3
    item_dict = {"id": item_id, "data": "hello"}
    item = Mock()
    item.idx = item_id
    item.to_dict.return_value = item_dict

    feed_name = "feed_name"
    feed_dict = Mock()
    feed = Mock()
    feed.to_dict.return_value = feed_dict
    feed.key = feed_name
    feed.updated_items = [item]

    db_item_document = Mock()
    db_item_collection = Mock()
    db_item_collection.document.return_value = db_item_document
    db_document_client = Mock()
    db_document_client.set = MagicMock()
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    sut.push_feed(feed)

    db_item_collection.document.assert_called_once_with(str(item_id))
    db_item_document.set.assert_called_once_with(item_dict)
    feed.clear_updated_items.assert_called_once()


def test_apply_feed_pushes_all_cached_feeds():
    feeds = {}
    documents = {}

    def document_client_provider(feed_name):
        db_document = Mock()
        db_document.exists = True
        db_document.to_dict = MagicMock()
        db_item_collection = Mock()
        db_item_collection.get.return_value = []
        db_document_client = Mock()
        db_document_client.get.return_value = db_document
        db_document_client.collection.return_value = db_item_collection
        documents[feed_name] = db_document_client
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=document_client_provider)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    sut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feed_mock.key = feed_name
        feed_mock.updated_items = []
        feeds[feed_name] = feed_mock
        with patch("email_exporter.feed_management.feed.Feed.from_data_and_items", MagicMock(return_value=feed_mock)):
            feed = sut.get_feed(feed_name)
        assert feed == feed_mock

    sut.apply_feeds()

    for feed in feeds.values():
        feed.update_rss.assert_called_once()

    for feed_name in feed_names:
        assert feed_name in documents
        documents[feed_name].set.assert_called_once()


def test_apply_feed_feed_throws_pushes_all_other_feeds():
    feeds = {}
    documents = {}

    def document_client_provider(feed_name):
        db_document = Mock()
        db_document.exists = True
        db_document.to_dict = MagicMock()
        db_item_collection = Mock()
        db_item_collection.get.return_value = []
        db_document_client = Mock()
        db_document_client.get.return_value = db_document
        db_document_client.collection.return_value = db_item_collection
        documents[feed_name] = db_document_client
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=document_client_provider)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    exception_feed_name = "exception_feed_name"
    feed_names = ["feed_name_1", exception_feed_name, "feed_name_2", "feed_name_3"]

    sut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feed_mock.key = feed_name
        feed_mock.updated_items = []
        feeds[feed_name] = feed_mock
        if feed_name == exception_feed_name:
            feed_mock.update_rss = MagicMock(side_effect=Exception("Test"))
        with patch("email_exporter.feed_management.feed.Feed.from_data_and_items", MagicMock(return_value=feed_mock)):
            feed = sut.get_feed(feed_name)
        assert feed == feed_mock

    sut.apply_feeds()

    for feed in feeds.values():
        feed.update_rss.assert_called_once()

    for feed_name in feed_names:
        if feed_name == exception_feed_name:
            continue
        assert feed_name in documents
        documents[feed_name].set.assert_called_once()


def test_apply_feed_with_prune_prunes_all_feeds():
    feeds = {}

    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    sut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feeds[feed_name] = feed_mock

        with patch("email_exporter.feed_management.feed.Feed.from_data_and_items", MagicMock(return_value=feed_mock)):
            feed = sut.get_feed(feed_name)
        assert feed == feed_mock

    sut.apply_feeds(prune=True)

    for feed in feeds.values():
        feed.prune.assert_called_once()


def test_apply_feed_without_prune_doesnt_prune_feeds():
    feeds = {}

    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    sut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feeds[feed_name] = feed_mock

        with patch("email_exporter.feed_management.feed.Feed.from_data_and_items", MagicMock(return_value=feed_mock)):
            feed = sut.get_feed(feed_name)
        assert feed == feed_mock

    sut.apply_feeds(prune=False)

    for feed in feeds.values():
        feed.prune.assert_not_called()


def test_delete_logs_error_if_not_flushed():
    logger = Mock()

    feed_name = "feed_name"

    db_document = Mock()
    db_document.to_dict.return_value = {}
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    sut = FeedProvider(
        Mock(), firestore_client,
        Mock(), logger
    )

    with patch("email_exporter.feed_management.feed.Feed.from_data_and_items", Mock()):
        sut.get_feed(feed_name)

    logger.error.assert_not_called()

    del sut

    logger.error.assert_called()


def test_add_feed_alias_created():
    feed_name = "feed_name"
    alias_name = "alias_name"
    bucket_name = "bucket_name"
    feed_doc = _create_document({"bucket_name": bucket_name})
    alias_doc = _create_document(None, exists=False)

    def get_document(key):
        if key == feed_name:
            return feed_doc
        if key == alias_name:
            return alias_doc
        raise KeyError()

    db_client = Mock()
    db_client.document = MagicMock(side_effect=get_document)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    sut.add_feed_alias(feed_name, alias_name)

    alias_doc.set.assert_called_once_with({"alias": feed_doc})


def test_add_feed_alias_key_exists_throws():
    feed_name = "feed_name"
    alias_name = "alias_name"
    bucket_name = "bucket_name"
    feed_doc = _create_document({"bucket_name": bucket_name})
    alias_doc = _create_document(None, exists=True)

    def get_document(key):
        if key == feed_name:
            return feed_doc
        if key == alias_name:
            return alias_doc
        raise KeyError()

    db_client = Mock()
    db_client.document = MagicMock(side_effect=get_document)
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    with pytest.raises(KeyError):
        sut.add_feed_alias(feed_name, alias_name)


def test_get_feed_uses_items_if_no_collection():
    bucket_name = "bucket_name"
    item_idx = 3

    db_document = Mock()
    db_document.exists = True
    db_document.to_dict.return_value = {
        "bucket_name": bucket_name,
        "items": [{"id": item_idx}]
    }
    db_item_collection = Mock()
    db_item_collection.get.return_value = []
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)

    assert len(feed.items) == 1
    assert feed.items[0].idx == item_idx


def test_get_feed_uses_collection_for_items():
    item_idx = 3

    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_item = Mock()
    db_item.to_dict.return_value = {"id": item_idx}
    db_item_collection = Mock()
    db_item_collection.get.return_value = [db_item]
    db_document_client = Mock()
    db_document_client.get.return_value = db_document
    db_document_client.collection.return_value = db_item_collection
    db_client = Mock()
    db_client.document.return_value = db_document_client
    firestore_client = Mock()
    firestore_client.collection.return_value = db_client

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get.return_value = collection_name

    sut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = sut.get_feed(feed_name)

    assert len(feed.items) == 1
    assert feed.items[0].idx == item_idx
