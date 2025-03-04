from dependency_injector import containers, providers

from src.config import Config
from src.logger import get_logger
from src.services import GptService, VideoGetterService, HuggingFaceService


class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Config)

    logger = providers.Callable(get_logger)

    gpt_service = providers.Singleton(GptService, config=config)

    huggingface_service = providers.Singleton(HuggingFaceService, config=config)

    video_getter_service = providers.Singleton(VideoGetterService, logger=logger("video_getter_service"))
