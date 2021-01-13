class EmailExporter:
    def __init__(self, config, feed_provider, t2s, parser):
        self.feed_file_name = config.get("FEED_FILE_NAME")
        self.config = config
        self.feed_provider = feed_provider
        self.t2s = t2s
        self.parser = parser
        self.feed_cache = {}

    def message_handler(self, sender, item):
        if sender in self.feed_cache:
            feed = feed_cache[sender]
        else:
            feed = self.feed_provider.get_feed(sender)
            self.feed_cache[sender] = feed

        if feed.bucket is None:
            return False

        content = list(self.parser.parse(item["soup"]))
        sound_data = self.t2s.lines_to_speech(content)

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
        for feed in self.feed_cache.values():
            self.feed_provider.push_feed(feed)
            feed.update_rss(self.feed_file_name)
        self.feed_cache = {}

    def __del__(self):
        if len(self.feed_cache) > 0:
            print("feeds not applied!")
