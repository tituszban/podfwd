from mock import Mock, MagicMock
from email_exporter.email_exporter import EmailExporter


def test_email_exporter_message_handler_returns_true_if_feed_is_None():
    feed_provider = Mock()
    feed_provider.get_feed = MagicMock(return_value=None)
    parser_selector = Mock()

    sut = EmailExporter(
        Mock(), feed_provider, Mock(), parser_selector, Mock(), Mock())

    owner = "content_item_owner"
    content_item = Mock()
    content_item.owner = owner

    result = sut.message_handler(content_item)

    feed_provider.get_feed.assert_called_once_with(owner)
    parser_selector.get_parser.assert_not_called()

    assert result is True


def test_email_exporter_message_handler_returns_false_if_feed_bucket_is_None():
    feed = Mock()
    feed.bucket = None
    feed_provider = Mock()
    feed_provider.get_feed = MagicMock(return_value=feed)
    parser_selector = Mock()

    sut = EmailExporter(
        Mock(), feed_provider, Mock(), parser_selector, Mock(), Mock())

    owner = "content_item_owner"
    content_item = Mock()
    content_item.owner = owner

    result = sut.message_handler(content_item)

    feed_provider.get_feed.assert_called_once_with(owner)
    parser_selector.get_parser.assert_not_called()

    assert result is False


def test_email_exporter_message_handler_calls_dependencies():
    feed = Mock()
    feed.bucket = Mock()
    feed.add_item_bytes = Mock()
    feed_provider = Mock()
    feed_provider.get_feed = MagicMock(return_value=feed)

    ssml = "ssml"
    description = ["description1", "description2"]
    parser = Mock()
    parser.parse = MagicMock(return_value=(ssml, description))
    parser_selector = Mock()
    parser_selector.get_parser = MagicMock(return_value=parser)

    voice = "voice"
    voice_provider = Mock()
    voice_provider.get_voice = MagicMock(return_value=voice)

    sound_data = "sound_data"
    t2s = Mock()
    t2s.lines_to_speech = MagicMock(return_value=sound_data)

    sut = EmailExporter(
        Mock(), feed_provider, t2s, parser_selector, Mock(), voice_provider)

    content_item = Mock()
    content_item.owner = "content_item_owner"
    content_item.title = "content_item_title"
    content_item.date = "content_item_date"
    content_item.sender = "content_item_sender"

    result = sut.message_handler(content_item)

    feed_provider.get_feed.assert_called_once_with(content_item.owner)

    parser_selector.get_parser.assert_called_once_with(content_item)
    parser.parse.assert_called_once_with(content_item)
    voice_provider.get_voice.assert_called_once_with(content_item)
    t2s.lines_to_speech.assert_called_once_with(ssml, voice)
    feed.add_item_bytes.assert_called_once_with(
        title=content_item.title,
        description='\n'.join(description),
        date=content_item.date,
        sender=content_item.sender,
        data=sound_data
    )

    assert result is True
