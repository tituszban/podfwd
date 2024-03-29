from email_exporter.config import Config
from logging import Logger
from firebase_admin.firestore import Client as FirestoreClient

from email_exporter.inbox import InboxItem

VOICE_DEFAULT = "en-US-Wavenet-A"
GLOBAL_DOCUMENT = "global"
GLOBAL_DOMAIN = "global"


class VoiceProvider:
    def __init__(
            self,
            config: Config,
            logger: Logger,
            firestore_client: FirestoreClient) -> None:
        self.collection = config.get("VOICES_COLLECTION")
        self._logger = logger
        self._db = firestore_client

    def get_voice(self, item: InboxItem):
        self._logger.info(f"Selecting voide for {item}")
        owner = item.owner
        sender = item.sender
        sender_domain = sender.split("@")[-1]

        voice_collection = self._db.collection(self.collection)
        global_settings = voice_collection.document(GLOBAL_DOCUMENT).get()
        owner_settings = voice_collection.document(owner).get()

        setting_providers = [provider.to_dict() for provider in [owner_settings, global_settings] if provider.exists]

        sources = []

        for key in [sender_domain, GLOBAL_DOMAIN]:
            for provider in setting_providers:
                if key in provider:
                    sources.append(provider[key])

        self._logger.info(f"Voice provider sources identified: {[s for source in sources for s in source.keys()]}")

        voice = self._match_source(sources, item)

        self._logger.info(f"Voice selected: {voice}")

        return voice

    def _match_source(self, sources: list[dict[str, list[dict]]], item: InboxItem, default: str = VOICE_DEFAULT) -> str:
        for source in sources:
            for voice, criteria in source.items():
                if self._match_criteria(criteria, item):
                    return voice
        return default

    def _match_criteria(self, criteria: list[dict], item: InboxItem):
        for rule in criteria:
            if all([self._match_rule(key, value, item) for key, value in rule.items()]):
                return True
        return False

    def _match_rule(self, key: str, value: str, item: InboxItem):
        def rule_always(value: str, _item: InboxItem):
            return bool(value)

        def rule_sender(value: str, _item: InboxItem):
            return _item.sender.split("@")[0] == value

        def rule_sender_contains(value: str, _item: InboxItem):
            return value in _item.sender.split("@")[0]

        def rule_subject_contains(value: str, _item: InboxItem):
            return value in _item.title.lower()

        def rule_default(value: str, _item: InboxItem):
            self._logger.error(f"Unknown voice provider rule: '{value}'")
            return False

        return {
            "always": rule_always,
            "sender": rule_sender,
            "sender_contains": rule_sender_contains,
            "subject_contains": rule_subject_contains
        }.get(key, rule_default)(value, item)
