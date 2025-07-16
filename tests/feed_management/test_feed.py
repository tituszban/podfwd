from mock import Mock, MagicMock, patch
from freezegun import freeze_time
import datetime
from email_exporter.feed_management.feed import Feed, Branding, Logo


def test_branding_from_dict_loads_fields():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    sut = Branding.from_dict(branding_dict)

    assert sut.author == author
    assert sut.email == email


def test_branding_from_dict_fills_in_values():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    sut = Branding.from_dict(branding_dict)

    assert sut.link is not None
    assert len(sut.link) > 0


def test_branding_from_dict_loads_nested_logo():
    logo_url = "logo_link_value"
    branding_dict = {
        "logo": {
            "url": logo_url
        }
    }

    sut = Branding.from_dict(branding_dict)

    assert isinstance(sut.logo, Logo)
    assert sut.logo.url == logo_url


def test_branding_to_dict_converts_fields():
    author = "author_value"
    email = "email_value"
    branding_dict = {
        "author": author,
        "email": email
    }

    sut = Branding.from_dict(branding_dict)
    result = sut.to_dict()

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

    sut = Branding.from_dict(branding_dict)
    result = sut.to_dict()

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

    sut = Feed.from_dict(feed_key, feed_data, Mock())

    assert sut.key == feed_key
    assert sut.bucket_name == bucket_name
    assert sut.item_lifetime_days == item_lifetime_days
    assert isinstance(sut.branding, Branding)
    assert sut.branding.author == author
    assert sut.feed_file_name == feed_file_name


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

    sut = Feed.from_dict(feed_key, feed_data, Mock())
    result = sut.to_dict()

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
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    raw_data = "raw_data_value"
    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    next_idx = feed.next_id
    file_name = f"{next_idx}.mp3"

    feed.add_item_bytes("title", "description", "date", "sender", raw_data, "mp3")

    bucket.upload_bytes.assert_called_once_with(file_name, raw_data)


def test_add_item_bytes_uses_bucket_url():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    raw_data = "raw_data_value"
    bucket_url = "bucket_url_value"
    bucket = Mock()
    bucket.upload_bytes.return_value = bucket_url
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    next_idx = feed.next_id
    file_name = f"{next_idx}.mp3"

    item = feed.add_item_bytes("title", "description", "date", "sender", raw_data, "mp3")

    assert item.file_info.url == bucket_url
    assert item.file_info.file_name == file_name
    assert item.file_info.is_external is False


def test_add_item_bytes_uses_passed_in_values():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    title = "title_value"
    description = "description_value"
    date = "date_value"
    sender = "sender_value"

    item = feed.add_item_bytes(title, description, date, sender, "raw_data_value", "mp3")

    assert item.title == title
    assert item.description == description
    assert item.date == date
    assert item.sender == sender


def test_add_item_bytes_created_date_is_now():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    date_now = datetime.datetime(2021, 7, 1)
    with freeze_time(date_now):
        item = feed.add_item_bytes("title", "description", "date", "sender", "raw_data_value", "mp3")

    assert item.created_date == date_now


def test_add_item_bytes_item_added_to_items():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    next_idx = feed.next_id

    item = feed.add_item_bytes("title", "description", "date", "sender", "raw_data_value", "mp3")

    assert item.idx == next_idx
    assert item in feed.items


def test_add_item_url_uses_specified_url():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    item_url = "bucket_url_value"

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    item = feed.add_item_url("title", "description", "date", "sender", item_url)

    assert item.file_info.url == item_url
    assert item.file_info.is_external is True


def test_add_item_url_uses_passed_in_values():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    title = "title_value"
    description = "description_value"
    date = "date_value"
    sender = "sender_value"

    item = feed.add_item_url(title, description, date, sender, "item_url")

    assert item.title == title
    assert item.description == description
    assert item.date == date
    assert item.sender == sender


def test_add_item_url_created_date_is_now():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    date_now = datetime.datetime(2021, 7, 1)
    with freeze_time(date_now):
        item = feed.add_item_url("title", "description", "date", "sender", "item_url")

    assert item.created_date == date_now


def test_add_item_url_item_added_to_items():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    next_idx = feed.next_id

    item = feed.add_item_url("title", "description", "date", "sender", "item_url")

    assert item.idx == next_idx
    assert item in feed.items


def test_add_item_file_path_calls_bucket():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    file_name = "file_name_value"
    file_path = f"path/to/file/{file_name}"
    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    feed.add_item_file_path("title", "description", "date", "sender", file_path)

    bucket.upload_from_file_path.assert_called_once_with(file_name, file_path)


def test_add_item_file_path_uses_bucket_url():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    file_name = "file_name_value"
    file_path = f"path/to/file/{file_name}"
    bucket_url = "bucket_url_value"
    bucket = Mock()
    bucket.upload_from_file_path.return_value = bucket_url
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    item = feed.add_item_file_path("title", "description", "date", "sender", file_path)

    assert item.file_info.url == bucket_url
    assert item.file_info.file_name == file_name
    assert item.file_info.is_external is False


def test_add_item_file_path_uses_passed_in_values():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    title = "title_value"
    description = "description_value"
    date = "date_value"
    sender = "sender_value"

    item = feed.add_item_file_path(title, description, date, sender, "file_path")

    assert item.title == title
    assert item.description == description
    assert item.date == date
    assert item.sender == sender


def test_add_item_file_path_created_date_is_now():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    date_now = datetime.datetime(2021, 7, 1)
    with freeze_time(date_now):
        item = feed.add_item_file_path("title", "description", "date", "sender", "file_path")

    assert item.created_date == date_now


def test_add_item_file_path_item_added_to_items():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    next_idx = feed.next_id

    item = feed.add_item_file_path("title", "description", "date", "sender", "file_path")

    assert item.idx == next_idx
    assert item in feed.items


def test_to_rss_calls_rss_gen():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    feed = Feed.from_dict(feed_key, feed_data, Mock())

    rss_value = "rss_value"
    generate_feed = MagicMock(return_value=rss_value)

    with patch("email_exporter.feed_management.rss_gen.generate_feed", generate_feed):
        result = feed.to_rss()

    generate_feed.assert_called_once()
    assert result == rss_value


def test_update_rss_uploads_to_bucket():
    feed_key = "feed_key_value"
    feed_file_name = "feed_file_name"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
        "feed_file_name": feed_file_name
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    rss_value = "rss_value"
    generate_feed = MagicMock(return_value=rss_value)

    with patch("email_exporter.feed_management.rss_gen.generate_feed", generate_feed):
        feed.update_rss()

    generate_feed.assert_called_once()
    bucket.upload_xml.assert_called_once_with(feed_file_name, rss_value)


def test_update_rss_no_bucket_no_conversion():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name"
    }

    storage_provider = Mock()
    storage_provider.get_bucket.return_value = None

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    rss_value = "rss_value"
    generate_feed = MagicMock(return_value=rss_value)

    with patch("email_exporter.feed_management.rss_gen.generate_feed", generate_feed):
        feed.update_rss()

    generate_feed.assert_not_called()


def test_prune_calls_bucket_delete():
    feed_key = "feed_key_value"
    deleted_file_name = "deleted_file_name"
    feed_data = {
        "items": [
            {
                "id": 1,
                "date": "Wed, 7 Jul 2021 08:00:00 +0000",
                "file_info": {
                    "file_name": deleted_file_name
                }
            }
        ],
        "bucket_name": "bucket_name",
        "item_lifetime_days": 7
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    assert len(feed.items) > 0
    assert feed.items[0].file_info.is_removed is False

    with freeze_time("2021-07-15"):
        feed.prune()

    bucket.delete_blob.assert_called_once_with(deleted_file_name)
    assert feed.items[0].file_info.is_removed is True


def test_prune_skips_files_within_lifetime():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [
            {
                "id": 1,
                "date": "Wed, 7 Jul 2021 08:00:00 +0000",
            }
        ],
        "bucket_name": "bucket_name",
        "item_lifetime_days": 7
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    assert len(feed.items) > 0
    assert feed.items[0].file_info.is_removed is False

    with freeze_time("2021-07-08"):
        feed.prune()

    bucket.delete_blob.assert_not_called()
    assert feed.items[0].file_info.is_removed is False


def test_prune_skips_external_files():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [
            {
                "id": 1,
                "date": "Wed, 7 Jul 2021 08:00:00 +0000",
                "file_info": {
                    "is_external": True
                }
            }
        ],
        "bucket_name": "bucket_name",
        "item_lifetime_days": 7
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    assert len(feed.items) > 0
    assert feed.items[0].file_info.is_removed is False

    with freeze_time("2021-07-15"):
        feed.prune()

    bucket.delete_blob.assert_not_called()
    assert feed.items[0].file_info.is_removed is False


def test_prune_skips_removed_files():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [
            {
                "id": 1,
                "date": "Wed, 7 Jul 2021 08:00:00 +0000",
                "file_info": {
                    "is_removed": True
                }
            }
        ],
        "bucket_name": "bucket_name",
        "item_lifetime_days": 7
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    assert len(feed.items) > 0
    assert feed.items[0].file_info.is_removed is True

    with freeze_time("2021-07-15"):
        feed.prune()

    bucket.delete_blob.assert_not_called()


def test_add_item_url_marks_item_as_updated():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    item = feed.add_item_url("title", "description", "date", "sender", "item_url")

    assert len(feed.updated_items) == 1
    assert feed.updated_items[0] == item


def test_prune_marks_pruned_item_as_updated():
    feed_key = "feed_key_value"
    item_id = 1
    feed_data = {
        "items": [
            {
                "id": item_id,
                "date": "Wed, 7 Jul 2021 08:00:00 +0000",
                "file_info": {
                    "file_name": "deleted_file_name"
                }
            }
        ],
        "bucket_name": "bucket_name",
        "item_lifetime_days": 7
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    assert len(feed.items) > 0
    assert feed.items[0].file_info.is_removed is False

    with freeze_time("2021-07-15"):
        feed.prune()

    assert len(feed.updated_items) == 1
    assert feed.updated_items[0].idx == item_id


def test_clear_updated_items_empties_updated_items():
    feed_key = "feed_key_value"
    feed_data = {
        "items": [],
        "bucket_name": "bucket_name",
    }

    bucket = Mock()
    storage_provider = Mock()
    storage_provider.get_bucket.return_value = bucket

    feed = Feed.from_dict(feed_key, feed_data, storage_provider)

    feed.add_item_url("title", "description", "date", "sender", "item_url")

    assert len(feed.updated_items) == 1

    feed.clear_updated_items()

    assert len(feed.updated_items) == 0
