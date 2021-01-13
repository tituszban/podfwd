import logging
from email_exporter import EmailExporter, Inbox, TextToSpeech, StorageProvider, FeedProvider, TcParser, Config


def main(request):
    config = Config()\
        .add_env_variables("AP_")

    logger_name = config.get("LOGGER_NAME", "email_exporter")
    logger = logging.getLogger(logger_name)

    t2s = TextToSpeech(config)
    storage = StorageProvider(config)
    feed_provider = FeedProvider(config, storage)
    inbox = Inbox(config, logger)
    parser = TcParser(logger)

    email_exporter = EmailExporter(
        config, feed_provider, t2s,
        parser, logger
    )

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success"


if __name__ == "__main__":
    main(None)
    # blob_test()
