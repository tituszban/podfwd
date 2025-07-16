from email_exporter.config import Config
from logging import Logger
from google.cloud.firestore import Client as FirestoreClient

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

    def get_voice(self, item: InboxItem, default: str = VOICE_DEFAULT) -> str:
        self._logger.info(f"Selecting voide for {item}")
        owner = item.owner
        sender = item.sender
        sender_address, sender_domain = sender.split("@")
        sender_root = sender_address.split("+")[0]

        voice_collection = self._db.collection(self.collection)
        global_settings = voice_collection.document(GLOBAL_DOCUMENT).get()
        owner_settings = voice_collection.document(owner).get()

        setting_providers = [
            (key.split("@"), value)
            for provider in [owner_settings, global_settings]
            if provider.exists
            for key, value in sorted(provider.to_dict().items(), reverse=True)
            if "@" in key
        ]

        for key, voice in setting_providers:
            root, domain = key
            if (root == sender_root or root == "*") and (domain == sender_domain or domain == "*"):
                self._logger.info(f"Matched voice {voice} for ({item.owner}/{item.sender})")
                return voice

        return default
