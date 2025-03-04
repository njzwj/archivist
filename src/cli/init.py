from src.container import Container


def init():
    container = Container()

    config = container.config()

    archivist_env_path = config.default_config_path

    logger = container.logger()
    if config.check_config_exists():
        logger.info(f"Config file already exists at {archivist_env_path}")
        return

    logger.info(f"Creating config file at {archivist_env_path}")
    config.write_config()
    logger.info(f"Config file created at {archivist_env_path}")
