from mock import Mock
from email_exporter.email_exporter import EmailExporter
from email_exporter.parsers import ParsedItem


def test_email_exporter_message_handler_returns_true_if_feed_is_None():
    feed_provider = Mock()
    feed_provider.get_feed.return_value = None
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
    feed_provider.get_feed.return_value = feed
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
    feed_provider.get_feed.return_value = feed

    ssml = "ssml"
    description = ["description1", "description2"]
    parser = Mock()
    parser.parse.return_value = (ParsedItem(ssml, description))
    parser_selector = Mock()
    parser_selector.get_parser.return_value = parser

    voice = "voice"
    voice_provider = Mock()
    voice_provider.get_voice.return_value = voice

    t2s_output = Mock()
    t2s_output.audio_content.return_value = "sound_data"
    t2s_output.extension = "mp3"
    t2s = Mock()
    t2s.lines_to_speech.return_value = t2s_output

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
        data=t2s_output.audio_content,
        extension=t2s_output.extension,
    )

    assert result is True
