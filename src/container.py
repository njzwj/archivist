from dependency_injector import containers, providers

from src.config import Config
from src.logger import get_logger
from src.services import GptProvider

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Config)

    logger = providers.Callable(get_logger)

    gpt_provider = providers.Singleton(GptProvider, config=config)
