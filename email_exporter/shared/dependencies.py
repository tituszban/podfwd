from ..email_exporter import EmailExporter
from ..inbox import Inbox
from ..cloud import TextToSpeech, StorageProvider
from ..feed_management import FeedProvider
from ..parsers import ParserSelector
from ..config import Config
from ..voice_provider import VoiceProvider
from firebase_admin import firestore
from firebase_admin import credentials
import firebase_admin
import logging


def config_resolver(_):
    return Config()\
        .add_env_variables("AP_")


def logger_resolver(dependencies):
    config = dependencies.get(Config)
    logger_name = config.get("LOGGER_NAME", "email_exporter")
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)
    return logger


def email_exporter_resolver(deps):
    return EmailExporter(
        deps.get(Config),
        deps.get(FeedProvider),
        deps.get(TextToSpeech),
        deps.get(ParserSelector),
        deps.get(logging.Logger),
        deps.get(VoiceProvider)
    )

def firestore_client_resolver(deps):
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


class Dependencies:
    def __init__(self, overrides={}):
        self._resolvers = {
            Config: config_resolver,
            logging.Logger: logger_resolver,
            TextToSpeech: lambda deps: TextToSpeech(deps.get(Config)),
            StorageProvider: lambda deps: StorageProvider(deps.get(Config)),
            FeedProvider: lambda deps: FeedProvider(deps.get(Config), deps.get(firestore.Client), deps.get(StorageProvider)),
            Inbox: lambda deps: Inbox(deps.get(Config), deps.get(logging.Logger)),
            ParserSelector: lambda deps: ParserSelector(deps.get(logging.Logger)),
            EmailExporter: email_exporter_resolver,
            firestore.Client: firestore_client_resolver,
            VoiceProvider: lambda deps: VoiceProvider(deps.get(Config), deps.get(logging.Logger), deps.get(firestore.Client)),
            **overrides
        }
        self._instances = {}

    def get(self, t):
        if t in self._instances:
            return self._instances[t]

        if t not in self._resolvers:
            raise KeyError(f"Could not find resolver for {t}")

        instance = self._resolvers[t](self)
        self._instances[t] = instance
        return instance
