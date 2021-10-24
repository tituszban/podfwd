from ..email_exporter import EmailExporter
from ..inbox import InboxProcessor
from ..shared import Dependencies
from ..parsers import ParserSelector, CreatorParserSelector
from ..voice_provider import VoiceProvider, CreatorVoiceProvider


def export_inbox():
    deps = Dependencies.default()\
        .add_override(ParserSelector, CreatorParserSelector)\
        .add_override(VoiceProvider, CreatorVoiceProvider)

    email_exporter = deps.get(EmailExporter)
    inbox = deps.get(InboxProcessor)

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success: Export inbox"
