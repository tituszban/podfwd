from .voice_provider import VoiceProvider, VOICE_DEFAULT

class CreatorVoiceProvider(VoiceProvider):
    def get_voice(self, item):
        owner = item.owner

        settings = self._db.collection(self.collection).document(owner).get()

        if not settings.exists:
            return VOICE_DEFAULT

        return settings.to_dict().get("voice", VOICE_DEFAULT)