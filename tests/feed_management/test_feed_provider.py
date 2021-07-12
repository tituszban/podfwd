from mock import Mock, MagicMock, patch
import pytest
from email_exporter.feed_management.feed_provider import FeedProvider


def test_get_feed_returns_from_collection():
    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_document_client = Mock()
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get = MagicMock(return_value=collection_name)

    dut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = dut.get_feed(feed_name)

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
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get = MagicMock(return_value=collection_name)

    dut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    with pytest.raises(KeyError):
        _ = dut.get_feed(feed_name)


def test_get_feed_called_again_returns_from_cache():
    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_document_client = Mock()
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_name = "feed_name"
    collection_name = "collection_name"
    config = Mock()
    config.get = MagicMock(return_value=collection_name)

    dut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    feed = dut.get_feed(feed_name)
    feed2 = dut.get_feed(feed_name)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(feed_name)
    db_document_client.get.assert_called_once()
    db_document.to_dict.assert_called_once()
    assert feed
    assert feed2 == feed


def test_push_feed_calls_collection_set():
    feed_name = "feed_name"
    feed_dict = Mock()
    feed = Mock()
    feed.to_dict = MagicMock(return_value=feed_dict)
    feed.key = feed_name

    db_document_client = Mock()
    db_document_client.set = MagicMock()
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    collection_name = "collection_name"
    config = Mock()
    config.get = MagicMock(return_value=collection_name)

    dut = FeedProvider(
        config, firestore_client,
        Mock(), Mock()
    )

    dut.push_feed(feed)

    firestore_client.collection.assert_called_once_with(collection_name)
    db_client.document.assert_called_once_with(feed_name)
    db_document_client.set.assert_called_once_with(feed_dict)


def test_apply_feed_pushes_all_cached_feeds():
    feeds = {}
    documents = {}

    def document_client_provider(feed_name):
        db_document = Mock()
        db_document.exists = True
        db_document.to_dict = MagicMock()
        db_document_client = Mock()
        db_document_client.get = MagicMock(return_value=db_document)
        documents[feed_name] = db_document_client
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=document_client_provider)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    dut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feed_mock.key = feed_name
        feeds[feed_name] = feed_mock
        with patch("email_exporter.feed_management.feed.Feed.from_dict", MagicMock(return_value=feed_mock)):
            feed = dut.get_feed(feed_name)
        assert feed == feed_mock

    dut.apply_feeds()

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
        db_document_client = Mock()
        db_document_client.get = MagicMock(return_value=db_document)
        documents[feed_name] = db_document_client
        return db_document_client

    db_client = Mock()
    db_client.document = MagicMock(side_effect=document_client_provider)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    exception_feed_name = "exception_feed_name"
    feed_names = ["feed_name_1", exception_feed_name, "feed_name_2", "feed_name_3"]

    dut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feed_mock.key = feed_name
        feeds[feed_name] = feed_mock
        if feed_name == exception_feed_name:
            feed_mock.update_rss = MagicMock(side_effect=Exception("Test"))
        with patch("email_exporter.feed_management.feed.Feed.from_dict", MagicMock(return_value=feed_mock)):
            feed = dut.get_feed(feed_name)
        assert feed == feed_mock

    dut.apply_feeds()

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
    db_document_client = Mock()
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    dut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feeds[feed_name] = feed_mock

        with patch("email_exporter.feed_management.feed.Feed.from_dict", MagicMock(return_value=feed_mock)):
            feed = dut.get_feed(feed_name)
        assert feed == feed_mock

    dut.apply_feeds(prune=True)

    for feed in feeds.values():
        feed.prune.assert_called_once()


def test_apply_feed_without_prune_doesnt_prune_feeds():
    feeds = {}

    db_document = Mock()
    db_document.exists = True
    db_document.to_dict = MagicMock()
    db_document_client = Mock()
    db_document_client.get = MagicMock(return_value=db_document)
    db_client = Mock()
    db_client.document = MagicMock(return_value=db_document_client)
    firestore_client = Mock()
    firestore_client.collection = MagicMock(return_value=db_client)

    feed_names = ["feed_name_1", "feed_name_2", "feed_name_3"]

    dut = FeedProvider(
        Mock(), firestore_client,
        Mock(), Mock()
    )

    for feed_name in feed_names:
        feed_mock = Mock()
        feeds[feed_name] = feed_mock

        with patch("email_exporter.feed_management.feed.Feed.from_dict", MagicMock(return_value=feed_mock)):
            feed = dut.get_feed(feed_name)
        assert feed == feed_mock

    dut.apply_feeds(prune=False)

    for feed in feeds.values():
        feed.prune.assert_not_called()


def test_delete_logs_error_if_not_flushed():
    logger = Mock()

    feed_name = "feed_name"

    dut = FeedProvider(
        Mock(), Mock(),
        Mock(), logger
    )

    with patch("email_exporter.feed_management.feed.Feed.from_dict", Mock()):
        dut.get_feed(feed_name)

    logger.error.assert_not_called()

    del dut

    logger.error.assert_called()
