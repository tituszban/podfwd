from email_exporter import EmailExporter, Inbox, TextToSpeech, StorageProvider, FeedProvider, TcParser, Config


def main(request):
    config = Config()\
        .add_env_variables("AP_")

    t2s = TextToSpeech(config)
    storage = StorageProvider(config)
    feed_provider = FeedProvider(config, storage)
    inbox = Inbox(config)
    parser = TcParser()

    email_exporter = EmailExporter(
        config, feed_provider, t2s,
        parser
    )

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success"


if __name__ == "__main__":
    main(None)
    # blob_test()
