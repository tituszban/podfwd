class EmailExporter:
    def __init__(self, config, feed_provider, t2s, parser, logger):
        self._feed_file_name = config.get("FEED_FILE_NAME")
        self._config = config
        self._feed_provider = feed_provider
        self._t2s = t2s
        self._parser = parser
        self._logger = logger
        self._feed_cache = {}

    def message_handler(self, sender, item):
        if sender in self._feed_cache:
            feed = feed_cache[sender]
        else:
            feed = self._feed_provider.get_feed(sender)
            self._feed_cache[sender] = feed

        if feed.bucket is None:
            return False

        content = list(self._parser.parse(item["soup"]))
        sound_data = self._t2s.lines_to_speech(content)

        idx = feed.next_id
        url = feed.bucket.upload_bytes(f"{idx}.mp3", sound_data)

        feed.add_item(
            item["title"],
            "",
            item["date"],
            url,
            idx
        )

        return True

    def apply_feeds(self):
        self._logger.info(f"Applying {len(self._feed_cache)} feeds")
        for feed in self._feed_cache.values():
            self._feed_provider.push_feed(feed)
            feed.update_rss(self._feed_file_name)
        self._feed_cache = {}
        self._logger.info("Feeds applied")

    def __del__(self):
        if len(self._feed_cache) > 0:
            self._logger.error(f"Feeds not flushed. Dropping {len(self._feed_cache)} feeds")
