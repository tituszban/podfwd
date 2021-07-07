class VoiceProvider:
    def __init__(self, config, logger, firestore_client):
        self.collection = config.get("VOICES_COLLECTION")
        self._logger = logger
        self._db = firestore_client

    def get_voice(self, item):
        owner = item.owner
        sender = item.sender
        sender_domain = sender.split("@")[-1]

        voice_collection = self._db.collection(self.collection)
        global_settings = voice_collection.document("global").get()
        owner_settings = voice_collection.document(owner).get()

        setting_providers = [provider.to_dict() for provider in [owner_settings, global_settings] if provider.exists]

        sources = []

        for key in [sender_domain, "global"]:
            for provider in setting_providers:
                if key in provider:
                    sources.append(provider[key])

        return self._match_source(sources, item)

    def _match_source(self, sources, item, default="en-US-Wavenet-A"):
        for source in sources:
            for voice, criteria in source.items():
                if self._match_criteria(criteria, item):
                    return voice
        return default

    def _match_criteria(self, criteria, item):
        for rule in criteria:
            if all([self._match_rule(key, value, item) for key, value in rule.items()]):
                return True
        return False

    def _match_rule(self, key, value, item):
        def rule_always(value, _item):
            return bool(value)

        def rule_sender(value, _item):
            return _item.sender.split("@")[0] == value

        def rule_sender_contains(value, _item):
            return value in _item.sender.split("@")[0]

        def rule_subject_contains(value, _item):
            return value in _item.title.lower()

        def rule_default(value, _item):
            self._logger.error(f"Unknown voice provider rule: '{value}'")
            return False

        return {
            "always": rule_always,
            "sender": rule_sender,
            "sender_contains": rule_sender_contains,
            "subject_contains": rule_subject_contains
        }.get(key, rule_default)(value, item)
