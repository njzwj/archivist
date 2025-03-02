import os
from dependency_injector import containers, providers

from src.config import Config

class Container(containers.DeclarativeContainer):

    config = providers.Singleton(Config)

def init():
    archivist_env_path = os.path.expanduser(
        os.getenv('ARCHIVIST_ENV_PATH', Config.default_config_path)
    )

    container = Container()
    config = container.config()
    if config.check_config_exists():
        print(f"Config file already exists at {archivist_env_path}")
        return
    
    print(f"Creating config file at {archivist_env_path}")
    config.write_config()
