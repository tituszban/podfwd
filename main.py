import logging
from email_exporter import EmailExporter, Inbox, TextToSpeech, StorageProvider, FeedProvider, ParserSelector, Config


def main(request):
    config = Config()\
        .add_env_variables("AP_")

    logger_name = config.get("LOGGER_NAME", "email_exporter")
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    t2s = TextToSpeech(config)
    storage = StorageProvider(config)
    feed_provider = FeedProvider(config, storage)
    inbox = Inbox(config, logger)
    parser_selector = ParserSelector(logger)

    email_exporter = EmailExporter(
        config, feed_provider, t2s,
        parser_selector, logger
    )

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success"


if __name__ == "__main__":
    main(None)
    # blob_test()
