from __future__ import annotations
from typing import Callable, TypeVar, Type
from ..config import Config
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
from google.cloud import storage
import logging
from pythonjsonlogger import jsonlogger
from datetime import datetime

T = TypeVar("T")

class CloudRunJsonFormatter(jsonlogger.JsonFormatter):
    def parse(self):
        return ["name", "message", "filename", "funcName", "lineno"]

    def add_fields(self, log_record, record, message_dict):
        now = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')
        log_record["timestamp"] = now
        log_record["severity"] = record.levelname
        super().add_fields(log_record, record, message_dict)


def config_resolver(_):
    return Config()\
        .add_env_variables("AP_")


def logger_resolver(context: Context) -> logging.Logger:
    default_logger_name = context.config.get("LOGGER_NAME", "email_exporter")
    logger_name = default_logger_name if context.parent_type is None else str(context.parent_type.__name__)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.INFO)

    if context.config.get_bool("HUMAN_READABLE_LOGS"):
        stream_formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        stream_handler.setFormatter(stream_formatter)
    else:
        stream_handler.setFormatter(CloudRunJsonFormatter())

    logger.addHandler(stream_handler)

    return logger


def firestore_client_resolver(context: Context) -> firestore.Client:
    json = context.config.get("SA_FILE")
    project_id = context.config.get("PROJECT_ID")

    if json:
        cred = credentials.Certificate(json)
        firebase_admin.initialize_app(cred)
    elif firebase_admin._DEFAULT_APP_NAME not in firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, options={
            'projectId': project_id,
        })

    return firestore.client()


def storage_client_resolver(context: Context) -> storage.Client:
    json = context.config.get("SA_FILE")
    if json:
        return storage.Client.from_service_account_json(json)
    else:
        return storage.Client()


class CachedResolver:
    def __init__(self):
        self._cache = {}

    def wrap_resolver(
            self,
            base_type: type,
            resolver: Callable[[Context], object]) -> Callable[[Context], object]:

        def wrapped_resolver(context):
            if base_type in self._cache:
                return self._cache[base_type]
            instance = resolver(context)
            self._cache[base_type] = instance
            return instance

        return wrapped_resolver


class Context:
    def __init__(self, dependencies: Dependencies, parent_type: type = None):
        self.dependencies = dependencies
        self.parent_type = parent_type

    def clone_with_parent(self, new_parent_type: type) -> Context:
        return Context(self.dependencies, new_parent_type)

    @property
    def config(self):
        return self.dependencies.get(Config)


class Dependencies:
    def __init__(self, cache_object_by_default=True):
        self._instances = {}
        self._type_overrides = {}
        self._resolvers = {}
        self._type_cache_rule = {}
        self._resolver_cache = CachedResolver()
        self._cache_by_default = cache_object_by_default

    def add_override(self, base_type: type, override_type: type, cached: bool = True) -> Dependencies:
        self._type_overrides[base_type] = override_type
        self._type_cache_rule[override_type] = cached
        return self

    def add_transient(self, base_type: type) -> Dependencies:
        self._type_cache_rule[base_type] = False
        return self

    def add_singleton(self, base_type: type) -> Dependencies:
        self._type_cache_rule[base_type] = True
        return self

    def add_resolver(self, base_type: type, resolver: Callable[[Context], object]) -> Dependencies:
        self._resolvers[base_type] = resolver
        return self

    def add_cached_resolver(self, base_type: type, resolver: Callable[[Context], object]) -> Dependencies:
        self._resolvers[base_type] = self._resolver_cache.wrap_resolver(base_type, resolver)
        return self

    @staticmethod
    def default() -> Dependencies:
        return Dependencies() \
            .add_cached_resolver(Config, config_resolver) \
            .add_resolver(logging.Logger, logger_resolver) \
            .add_cached_resolver(firestore.Client, firestore_client_resolver) \
            .add_cached_resolver(storage.Client, storage_client_resolver)

    def get(self, t: Type[T], context: Context = None) -> T:
        if context is None:
            context = Context(self, t)

        if t in self._resolvers:
            return self._resolvers[t](context)

        if t in self._type_overrides:
            return self.get(self._type_overrides[t], context)

        if t in self._instances:
            return self._instances[t]

        if not hasattr(t, "__init__"):
            raise KeyError(f"No init method found on type {t}")

        if len(annotations := t.__init__.__annotations__) == 0:
            raise KeyError(f"No annotations found on the constructor for type {t}")

        instance = t(**{
            a_name: self.get(a_type, context.clone_with_parent(t))
            for a_name, a_type in annotations.items()
            if a_name != "return"
        })          # type: ignore

        if self._type_cache_rule.get(t, self._cache_by_default):
            self._instances[t] = instance

        return instance
