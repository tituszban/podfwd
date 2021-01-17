class EmailExporter:
    def __init__(self, config, feed_provider, t2s, parser, logger):
        self._feed_file_name = config.get("FEED_FILE_NAME")
        self._config = config
        self._feed_provider = feed_provider
        self._t2s = t2s
        self._parser_selector = parser
        self._logger = logger
        self._feed_cache = {}

    def _get_feed(self, owner):
        if owner in self._feed_cache:
            return self._feed_cache[owner]
        else:
            feed = self._feed_provider.get_feed(owner)
            if feed is not None:
                self._feed_cache[owner] = feed
            return feed

    def message_handler(self, addresses, item):
        owner, sender = addresses

        feed = self._get_feed(owner)

        if feed is None:
            self._logger.warn(
                f"Unrecognised email address: [{owner}] has no feed. Subject: [{item['title']}]; Sender: [{sender}]")
            return True

        if feed.bucket is None:
            self._logger.warn(
                f"No bucket found: [{owner}] has no allocated bucket")
            return False

        parser = self._parser_selector.get_parser(sender)
        ssml, description, voice = parser.parse(**item)

        sound_data = self._t2s.lines_to_speech(ssml, voice)

        idx = feed.next_id

        item = feed.add_item(
            title=item["title"],
            description='\n'.join(description),
            date=item["date"],
            url="",
            idx=idx,
            sender=sender
        )

        item.url = feed.bucket.upload_bytes(item.file_name, sound_data)

        return True

    def apply_feeds(self):
        self._logger.info(f"Applying {len(self._feed_cache)} feeds")
        applied_fileds = set()
        for key, feed in self._feed_cache.items():
            try:
                feed.prune()
                self._feed_provider.push_feed(feed)
                feed.update_rss(self._feed_file_name)
                applied_fileds.add(key)
            except:
                self._logger.exception(f"While applying feed [{key}] an error occured")
        
        for key in applied_fileds:
            self._feed_cache.pop(key)

        self._logger.info(f"Feeds applied: {len(applied_fileds)} feeds updated")

    def __del__(self):
        if len(self._feed_cache) > 0:
            self._logger.error(
                f"Feeds not flushed. Dropping {len(self._feed_cache)} feeds")
