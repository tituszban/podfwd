from ..email_exporter import EmailExporter
from ..inbox import InboxProcessor
from ..shared import Dependencies


def export_inbox():
    deps = Dependencies()

    email_exporter = deps.get(EmailExporter)
    inbox = deps.get(InboxProcessor)

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success: Export inbox"
