from mock import Mock, MagicMock, patch
import pytest
from email_exporter.feed_management.feed import Feed, Branding, Logo
from email_exporter.feed_management.item import Item


def test_branding_from_dict_loads_fields():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    dut = Branding.from_dict(branding_dict)

    assert dut.author == author
    assert dut.email == email


def test_branding_from_dict_fills_in_values():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    dut = Branding.from_dict(branding_dict)

    assert dut.link is not None
    assert len(dut.link) > 0


def test_branding_from_dict_loads_nested_logo():
    logo_url = "logo_link_value"
    branding_dict = {
        "logo": {
            "url": logo_url
        }
    }

    dut = Branding.from_dict(branding_dict)

    assert isinstance(dut.logo, Logo)
    assert dut.logo.url == logo_url


def test_branding_to_dict_converts_fields():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    dut = Branding.from_dict(branding_dict)
    result = dut.to_dict()

    assert "author" in result
    assert result["author"] == author
    assert "email" in result
    assert result["email"] == email


def test_branding_to_dict_converts_logo_fields():
    logo_url = "logo_link_value"
    branding_dict = {
        "logo": {
            "url": logo_url
        }
    }

    dut = Branding.from_dict(branding_dict)
    result = dut.to_dict()

    assert "logo" in result
    assert "url" in result["logo"]
    assert result["logo"]["url"] == logo_url


def test_feed_from_dict_loads_fields():
    feed_key = "feed_key_value"
    bucket_name = "bucket_name"
    item_lifetime_days = 99
    author = "author_value"
    feed_file_name = "feed_file_name_value"
    feed_data = {
        "items": [],
        "bucket_name": bucket_name,
        "item_lifetime_days": item_lifetime_days,
        "branding": {
            "author": author
        },
        "feed_file_name": feed_file_name
    }

    dut = Feed.from_dict(feed_key, feed_data, Mock())

    assert dut.key == feed_key
    assert dut.bucket_name == bucket_name
    assert dut.item_lifetime_days == item_lifetime_days
    assert isinstance(dut.branding, Branding)
    assert dut.branding.author == author
    assert dut.feed_file_name == feed_file_name


def test_feed_from_dict_fetches_bucket():
    feed_key = "feed_key_value"
    bucket_name = "bucket_name"
    feed_data = {
        "items": [],
        "bucket_name": bucket_name,
    }

    storage_provider = Mock()

    Feed.from_dict(feed_key, feed_data, storage_provider)

    storage_provider.get_bucket.assert_called_once_with(bucket_name)


def test_feed_to_dict_converts_fields():
    feed_key = "feed_key_value"
    bucket_name = "bucket_name"
    item_lifetime_days = 99
    author = "author_value"
    feed_file_name = "feed_file_name_value"
    feed_data = {
        "items": [],
        "bucket_name": bucket_name,
        "item_lifetime_days": item_lifetime_days,
        "branding": {
            "author": author
        },
        "feed_file_name": feed_file_name
    }

    dut = Feed.from_dict(feed_key, feed_data, Mock())
    result = dut.to_dict()

    assert "items" in result
    assert len(result["items"]) == 0
    assert "bucket_name" in result
    assert result["bucket_name"] == bucket_name
    assert "item_lifetime_days" in result
    assert result["item_lifetime_days"] == item_lifetime_days
    assert "branding" in result
    assert "feed_file_name" in result
    assert result["feed_file_name"] == feed_file_name


def test_next_id_is_zero_if_no_items():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    assert feed.next_id == 0


def test_next_id_is_greater_than_existing_ids():
    feed_key = "feed_key_value"
    idx = 99
    feed_data = {
        "items": [{"id": idx}],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    assert feed.next_id > idx


def test_add_item_bytes_calls_bucket():
    feed_key = "feed_key_value"
    bucket_name = "bucket_name"
    feed_data = {
        "items": [],
        "bucket_name": bucket_name,
    }

    raw_data = "raw_data_value"
    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket = MagicMock(return_value=bucket)

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    next_idx = feed.next_id
    file_name = Item.filename_from_id(next_idx)

    feed.add_item_bytes("title", "description", "date", "sender", raw_data)

    bucket.upload_bytes.assert_called_once_with(file_name, raw_data)
