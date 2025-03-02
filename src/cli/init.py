import os
from dependency_injector import containers, providers

from src.config import Config
from src.logger import get_logger

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Config)

    logger = providers.Callable(get_logger)

def init():
    archivist_env_path = os.path.expanduser(
        os.getenv('ARCHIVIST_ENV_PATH', Config.default_config_path)
    )

    container = Container()
    config = container.config()
    logger = container.logger()
    if config.check_config_exists():
        logger.info(f"Config file already exists at {archivist_env_path}")
        return
    
    logger.info(f"Creating config file at {archivist_env_path}")
    config.write_config()
    logger.info(f"Config file created at {archivist_env_path}")
