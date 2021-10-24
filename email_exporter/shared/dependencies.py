from __future__ import annotations
from typing import Callable
from ..email_exporter import EmailExporter
from ..cloud import TextToSpeech
from ..feed_management import FeedProvider
from ..parsers import ParserSelector
from ..config import Config
from ..voice_provider import VoiceProvider
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
import logging


def config_resolver(*_):
    return Config()\
        .add_env_variables("AP_")


def logger_type_resolver(dependencies: Dependencies, parent_type: type):
    return logger_resolver(dependencies, str(parent_type.__name__))


def logger_resolver(dependencies: Dependencies, logger_name=None):
    config = dependencies.get(Config)
    logger_name = config.get("LOGGER_NAME", "email_exporter") if logger_name is None else logger_name
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)
    stream_formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
    stream_handler.setFormatter(stream_formatter)

    logger.addHandler(stream_handler)

    return logger


def firestore_client_resolver(deps, *args):
    config = deps.get(Config)
    json = config.get("SA_FILE")
    project_id = config.get("PROJECT_ID")

    if json:
        cred = credentials.Certificate(json)
        firebase_admin.initialize_app(cred)
    elif firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, options={
            'projectId': project_id,
        })

    return firestore.client()


class CachedResolver:
    def __init__(self):
        self._cache = {}

    def wrap_resolver(
            self,
            base_type: type,
            resolver: Callable[[Dependencies, type], object]) -> Callable[[Dependencies, type], object]:
        def wrapped_resolver(*args):
            if base_type in self._cache:
                return self._cache[base_type]
            instance = resolver(*args)
            self._cache[base_type] = instance
            return instance
        return wrapped_resolver


def email_exporter_resolver(deps):
    return EmailExporter(
        deps.get(Config),
        deps.get(FeedProvider),
        deps.get(TextToSpeech),
        deps.get(ParserSelector),
        deps.get(logging.Logger),
        deps.get(VoiceProvider)
    )


def general_resolver(cls, dep_cls):
    def resolver(deps):
        return cls(*[deps.get(c) for c in dep_cls])
    return resolver


class Dependencies:
    def __init__(self):
        self._instances = {}
        self._type_overrides = {}
        self._type_resolvers = {}
        self._resolver_cache = CachedResolver()

    def add_override(self, base_type: type, override_type: type) -> Dependencies:
        self._type_overrides[base_type] = override_type
        return self

    def add_resolver(self, base_type: type, resolver: Callable[[Dependencies, type], object]) -> Dependencies:
        self._type_resolvers[base_type] = resolver
        return self

    def add_cached_resolver(self, base_type: type, resolver: Callable[[Dependencies, type], object]) -> Dependencies:
        self._type_resolvers[base_type] = self._resolver_cache.wrap_resolver(base_type, resolver)
        return self

    @staticmethod
    def default() -> Dependencies:
        return Dependencies() \
            .add_cached_resolver(Config, config_resolver) \
            .add_resolver(logging.Logger, logger_type_resolver) \
            .add_cached_resolver(firestore.Client, firestore_client_resolver)

    def _resolve_from_annotation(self, t):
        annotations = t.__init__.__annotations__

        def get_instance_for_type(a_type):
            if a_type in self._type_resolvers:
                return self._type_resolvers[a_type](self, t)
            if a_type in self._type_overrides:
                return self.get(self._type_overrides[a_type])
            return self.get(a_type)

        return t(**{
            a_name: get_instance_for_type(a_type)
            for a_name, a_type in annotations.items()
            if a_name != "return"
        })

    def get(self, t: type) -> object:
        if t in self._instances:
            return self._instances[t]

        if hasattr(t, "__init__") and len(list(filter(lambda a: a != "return", t.__init__.__annotations__))) > 0:
            instance = self._resolve_from_annotation(t)
        elif t in self._type_resolvers:
            instance = self._type_resolvers[t](self, t)
        elif t in self._type_overrides:
            instance = self.get(self._type_overrides[t])
        else:
            raise KeyError(f"Could not find resolver for {t}")

        self._instances[t] = instance
        return instance
