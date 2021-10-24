from .voice_provider import VoiceProvider, VOICE_DEFAULT

VOICE_KEY = "voice"


class CreatorVoiceProvider(VoiceProvider):
    def get_voice(self, item):
        self._logger.info(f"Selecting voide for {item}")
        owner = item.owner

        settings = self._db.collection(self.collection).document(owner).get()

        if not settings.exists:
            self._logger.info(f"No voice settings found for {owner}; Using default: {VOICE_DEFAULT}")
            return VOICE_DEFAULT

        voice = settings.to_dict().get(VOICE_KEY, VOICE_DEFAULT)

        self._logger.info(f"Voice selected from settings: {voice}")

        return voice
