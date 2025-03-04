import os

from src.container import Container

def debug(url):
    container = Container()

    output_path = os.path.expanduser("~/Downloads")
    
    logger = container.logger("debug")
    video_getter = container.video_getter_service()

    file_path = video_getter.download_video(url, output_path)

    if file_path:
        logger.info(f"Video downloaded to {file_path}")
    else:
        logger.error("Failed to download video")

    audio_path = video_getter.extract_audio(file_path, output_path)

    if audio_path:
        logger.info(f"Audio extracted to {audio_path}")
    else:
        logger.error("Failed to extract audio")
    
    return file_path
