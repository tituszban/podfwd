import logging
from ..email_exporter import EmailExporter
from ..inbox import Inbox
from ..shared import Dependencies
from ..config import Config
from firebase_admin import firestore
from ..parsers import ParserSelector, CreatorParserSelector
from ..voice_provider import VoiceProvider, CreatorVoiceProvider


def export_inbox():
    deps = Dependencies({
        ParserSelector: lambda deps: CreatorParserSelector(deps.get(logging.Logger)),
        VoiceProvider: lambda deps: CreatorVoiceProvider(
            deps.get(Config), deps.get(logging.Logger), deps.get(firestore.Client))
    })

    email_exporter = deps.get(EmailExporter)
    inbox = deps.get(Inbox)

    inbox.process_inbox(email_exporter.message_handler)

    email_exporter.apply_feeds()

    return "Success: Export inbox"
