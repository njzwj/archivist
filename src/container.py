from dependency_injector import containers, providers

from src.config import Config
from src.logger import get_logger
from src.services import (
    GptService,
    VideoGetterService,
    HuggingfaceService,
    ScrapeService,
    ExtractorService,
)


class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Config)

    logger = providers.Callable(get_logger)

    gpt_service = providers.Singleton(GptService, config=config)

    scrape_service = providers.Singleton(
        ScrapeService, gpt=gpt_service, logger=logger("scrape_service")
    )

    huggingface_service = providers.Singleton(
        HuggingfaceService, config=config, logger=logger("huggingface_service")
    )

    video_getter_service = providers.Singleton(
        VideoGetterService, logger=logger("video_getter_service")
    )

    extractor_service = providers.Singleton(
        ExtractorService,
        gpt=gpt_service,
        config=config,
        logger=logger("extractor_service"),
    )
