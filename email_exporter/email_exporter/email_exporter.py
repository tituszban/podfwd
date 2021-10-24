from email_exporter.config import Config
from email_exporter.feed_management import FeedProvider
from email_exporter.cloud import TextToSpeech
from email_exporter.parsers import ParserSelector
from email_exporter.voice_provider import VoiceProvider
from logging import Logger


class EmailExporter:
    def __init__(
            self,
            config: Config,
            feed_provider: FeedProvider,
            t2s: TextToSpeech,
            parser_selector: ParserSelector,
            logger: Logger,
            voice_provider: VoiceProvider) -> None:
        self._config = config
        self._feed_provider = feed_provider
        self._t2s = t2s
        self._parser_selector = parser_selector
        self._logger = logger
        self._voice_provider = voice_provider

    def message_handler(self, inbox_item):
        self._logger.info(f"Handling message: {inbox_item}")
        feed = self._feed_provider.get_feed(inbox_item.owner)

        if feed is None:
            self._logger.warn(
                "Unrecognised email address: [{}] has no feed. Subject: [{}]; Sender: [{}]".format(
                    inbox_item.owner, inbox_item.title, inbox_item.sender
                ))
            return True

        if feed.bucket is None:
            self._logger.warn(
                f"No bucket found: [{inbox_item.owner}] has no allocated bucket")
            return False
        self._logger.info(f"Feed found: {feed.key}")

        parser = self._parser_selector.get_parser(inbox_item)
        parsed_item = parser.parse(inbox_item)
        voice = self._voice_provider.get_voice(inbox_item)

        sound_data = self._t2s.lines_to_speech(parsed_item.ssml, voice)

        feed.add_item_bytes(
            title=inbox_item.title,
            description=parsed_item.combined_description,
            date=inbox_item.date,
            sender=inbox_item.sender,
            data=sound_data
        )

        return True

    def apply_feeds(self):
        self._feed_provider.apply_feeds()
