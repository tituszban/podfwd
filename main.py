from email_exporter.dependencies import Dependencies
import logging
from email_exporter import EmailExporter, Inbox, TextToSpeech, StorageProvider, FeedProvider, ParserSelector, Config, Dependencies


def main(request):
    deps = Dependencies()

    email_exporter = deps.get(EmailExporter)
    inbox = deps.get(Inbox)

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success"


if __name__ == "__main__":
    main(None)
    # blob_test()
