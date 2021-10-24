class EmailExporter:
    def __init__(self, config, feed_provider, t2s, parser, logger, voice_provider):
        self._config = config
        self._feed_provider = feed_provider
        self._t2s = t2s
        self._parser_selector = parser
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
        ssml, description = parser.parse(inbox_item)
        voice = self._voice_provider.get_voice(inbox_item)

        sound_data = self._t2s.lines_to_speech(ssml, voice)

        feed.add_item_bytes(
            title=inbox_item.title,
            description='\n'.join(description),
            date=inbox_item.date,
            sender=inbox_item.sender,
            data=sound_data
        )

        return True

    def apply_feeds(self):
        self._feed_provider.apply_feeds()
