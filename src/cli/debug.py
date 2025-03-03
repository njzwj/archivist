import os

from src.container import Container

def debug(url):
    container = Container()
    
    logger = container.logger("debug")
    video_getter = container.video_getter_service()
    file_path = video_getter.download_video(url, os.path.expanduser("~/Downloads"))

    if file_path:
        logger.info(f"Video downloaded to {file_path}")
    else:
        logger.error("Failed to download video")
    return file_path
