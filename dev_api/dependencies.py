"""
Dependency injection for dev_api.

Uses the same Dependencies pattern as the main email_exporter service,
extending it with dev-specific services.
"""
import os
import logging
from typing import Optional

from email_exporter.shared import Dependencies
from email_exporter.shared.dependencies import Context
from email_exporter.config import Config
from email_exporter.parsers import ParserSelector
from email_exporter.voice_provider import VoiceProvider

from .services.storage import DevStorage, AudioCache
from .services.email_loader import EmailLoader
from .services.parser_service import ParserService


class DevConfig:
    """Dev-specific configuration paths."""
    def __init__(self, config: Config):
        self._config = config
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        
        self.sources_folder = os.path.join(base_path, "sources")
        self.dev_data_folder = os.path.join(base_path, "dev_data")
        self.audio_cache_folder = os.path.join(self.dev_data_folder, "audio_cache")
        
        # Ensure directories exist
        os.makedirs(self.dev_data_folder, exist_ok=True)
        os.makedirs(self.audio_cache_folder, exist_ok=True)

    @property
    def config(self) -> Config:
        return self._config


def dev_config_resolver(context: Context) -> DevConfig:
    config = context.dependencies.get(Config)
    return DevConfig(config)


def dev_storage_resolver(context: Context) -> DevStorage:
    dev_config = context.dependencies.get(DevConfig)
    return DevStorage(dev_config.dev_data_folder)


def audio_cache_resolver(context: Context) -> AudioCache:
    dev_config = context.dependencies.get(DevConfig)
    storage = context.dependencies.get(DevStorage)
    return AudioCache(dev_config.audio_cache_folder, storage)


def email_loader_resolver(context: Context) -> EmailLoader:
    dev_config = context.dependencies.get(DevConfig)
    storage = context.dependencies.get(DevStorage)
    config = context.dependencies.get(Config)
    logger = context.dependencies.get(logging.Logger)
    return EmailLoader(
        sources_folder=dev_config.sources_folder,
        storage=storage,
        config=config,
        logger=logger
    )


def parser_service_resolver(context: Context) -> ParserService:
    logger = context.dependencies.get(logging.Logger)
    parser_selector = context.dependencies.get(ParserSelector)
    voice_provider = context.dependencies.get(VoiceProvider)
    return ParserService(
        logger=logger,
        parser_selector=parser_selector,
        voice_provider=voice_provider
    )


def parser_selector_resolver(context: Context) -> ParserSelector:
    logger = context.dependencies.get(logging.Logger)
    return ParserSelector(logger)


def dev_logger_resolver(context: Context) -> logging.Logger:
    """Logger configured for dev UI with human-readable output."""
    logger_name = "dev_api" if context.parent_type is None else context.parent_type.__name__
    logger = logging.getLogger(logger_name)
    
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        handler = logging.StreamHandler()
        handler.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [%(name)s] [%(levelname)s] %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    return logger


def get_dev_dependencies() -> Dependencies:
    """
    Create Dependencies configured for dev_api.
    
    Extends the default production dependencies with dev-specific services.
    """
    return Dependencies.default() \
        .add_resolver(logging.Logger, dev_logger_resolver) \
        .add_cached_resolver(DevConfig, dev_config_resolver) \
        .add_cached_resolver(DevStorage, dev_storage_resolver) \
        .add_cached_resolver(AudioCache, audio_cache_resolver) \
        .add_cached_resolver(ParserSelector, parser_selector_resolver) \
        .add_cached_resolver(EmailLoader, email_loader_resolver) \
        .add_cached_resolver(ParserService, parser_service_resolver)


# Singleton dependencies instance for the app
_deps: Optional[Dependencies] = None


def get_dependencies() -> Dependencies:
    """Get or create the singleton Dependencies instance."""
    global _deps
    if _deps is None:
        _deps = get_dev_dependencies()
    return _deps


def reset_dependencies():
    """Reset dependencies (useful for testing or hot-reload)."""
    global _deps
    _deps = None
