import os
import hashlib
import json


class DevStorage:
    """Key-value storage for dev UI state using JSON file."""

    def __init__(self, data_folder: str):
        self._data_folder = data_folder
        self._db_path = os.path.join(data_folder, "dev_storage.json")
        self._data = self._load()

    def _load(self) -> dict:
        if os.path.exists(self._db_path):
            try:
                with open(self._db_path, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save(self):
        with open(self._db_path, 'w') as f:
            json.dump(self._data, f, indent=2)

    def get(self, key: str, default=None):
        return self._data.get(key, default)

    def set(self, key: str, value):
        self._data[key] = value
        self._save()

    def delete(self, key: str):
        if key in self._data:
            del self._data[key]
            self._save()

    def exists(self, key: str) -> bool:
        return key in self._data

    def get_all_keys(self, prefix: str = "") -> list[str]:
        if prefix:
            return [k for k in self._data.keys() if k.startswith(prefix)]
        return list(self._data.keys())


class AudioCache:
    """Cache for generated audio files, keyed by SSML content hash."""

    def __init__(self, cache_folder: str, storage: DevStorage):
        self._cache_folder = cache_folder
        self._storage = storage
        os.makedirs(cache_folder, exist_ok=True)

    def _get_cache_key(self, ssml: str, voice: str) -> str:
        content = f"{voice}:{ssml}"
        return hashlib.sha256(content.encode()).hexdigest()

    def get_audio_path(self, ssml: str, voice: str) -> str | None:
        cache_key = self._get_cache_key(ssml, voice)
        metadata = self._storage.get(f"audio_cache:{cache_key}")
        if metadata:
            audio_path = os.path.join(self._cache_folder, f"{cache_key}.{metadata['extension']}")
            if os.path.exists(audio_path):
                return audio_path
        return None

    def store_audio(self, ssml: str, voice: str, audio_data: bytes, extension: str) -> str:
        cache_key = self._get_cache_key(ssml, voice)
        audio_path = os.path.join(self._cache_folder, f"{cache_key}.{extension}")

        with open(audio_path, "wb") as f:
            f.write(audio_data)

        self._storage.set(f"audio_cache:{cache_key}", {
            "ssml": ssml,
            "voice": voice,
            "extension": extension
        })

        return audio_path

    def clear_cache(self):
        for key in self._storage.get_all_keys("audio_cache:"):
            self._storage.delete(key)
        for f in os.listdir(self._cache_folder):
            os.remove(os.path.join(self._cache_folder, f))
