class EmailExporter:
    def __init__(self, config, feed_provider, t2s, parser, logger, voice_provider):
        self._config = config
        self._feed_provider = feed_provider
        self._t2s = t2s
        self._parser_selector = parser
        self._logger = logger
        self._voice_provider = voice_provider

    def message_handler(self, content_item):
        feed = self._feed_provider.get_feed(content_item.owner)

        if feed is None:
            self._logger.warn(
                "Unrecognised email address: [{}] has no feed. Subject: [{}]; Sender: [{}]".format(
                    content_item.owner, content_item.title, content_item.sender
                ))
            return True

        if feed.bucket is None:
            self._logger.warn(
                f"No bucket found: [{content_item.owner}] has no allocated bucket")
            return False

        parser = self._parser_selector.get_parser(content_item)
        ssml, description = parser.parse(content_item)
        voice = self._voice_provider.get_voice(content_item)

        sound_data = self._t2s.lines_to_speech(ssml, voice)

        feed.add_item_bytes(
            title=content_item.title,
            description='\n'.join(description),
            date=content_item.date,
            sender=content_item.sender,
            data=sound_data
        )

        return True

    def apply_feeds(self):
        self._feed_provider.apply_feeds()
