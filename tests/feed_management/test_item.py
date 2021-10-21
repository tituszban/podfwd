import pytest
import datetime
from email_exporter.feed_management.item import Item, FileInfo


def test_from_dict_loads_fields():
    title = "author_value"
    sender = "email_value"
    idx = 10
    item_dict = {
        "title": title,
        "sender": sender,
        "id": idx
    }

    sut = Item.from_dict(item_dict)

    assert sut.title == title
    assert sut.sender == sender
    assert sut.idx == idx


def test_from_dict_default_is_None():
    title = "author_value"
    sender = "email_value"
    item_dict = {
        "title": title,
        "sender": sender
    }

    sut = Item.from_dict(item_dict)

    assert sut.description is None


def test_from_dict_loads_file_info_fields():
    item_url = "item_url"
    file_name = "file_name"
    item_dict = {
        "file_info": {
            "url": item_url,
            "file_name": file_name
        }
    }

    sut = Item.from_dict(item_dict)

    assert isinstance(sut.file_info, FileInfo)
    assert sut.file_info.url == item_url
    assert sut.file_info.file_name == file_name
    assert sut.file_info.is_external is False
    assert sut.file_info.is_removed is False


def test_from_dict_loads_file_info_from_url():
    file_name = "file_name"
    item_url = f"item/url/{file_name}"
    item_dict = {
        "url": item_url
    }

    sut = Item.from_dict(item_dict)

    assert sut.file_info.url == item_url
    assert sut.file_info.file_name == file_name


def test_to_dict_converts_fields():
    item_url = "item_url"
    file_name = "file_name"
    title = "author_value"
    sender = "email_value"
    item_dict = {
        "title": title,
        "sender": sender,
        "file_info": {
            "url": item_url,
            "file_name": file_name
        }
    }

    sut = Item.from_dict(item_dict)

    result = sut.to_dict()

    assert result["title"] == title
    assert result["sender"] == sender
    assert result["file_info"]["url"] == item_url
    assert result["file_info"]["file_name"] == file_name


@pytest.mark.parametrize("date", (
    ("Wed, 7 Jul 2021 08:00:00 +0000"),
    ("Wed, 7 Jul 2021 08:00:00 +0000 GMT"),
))
def test_try_get_date_correct_formats_handled(date):
    item_dict = {
        "date": date
    }

    sut = Item.from_dict(item_dict)

    result = sut.try_get_date()

    assert result == datetime.datetime(2021, 7, 7, 8)


def test_try_get_date_incorrect_format_throws():
    item_dict = {
        "date": "2021-07-07T08:00:00Z"
    }

    sut = Item.from_dict(item_dict)

    with pytest.raises(ValueError):
        sut.try_get_date()
