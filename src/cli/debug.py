import os

from src.container import Container

def debug(url):
    container = Container()

    output_path = os.path.expanduser("~/Downloads")
    
    logger = container.logger("debug")
    video_getter = container.video_getter_service()
    scraper = container.scrape_service()
    huggingface = container.huggingface_service()

    # test download video
    file_path = video_getter.download_video(url, output_path)

    if file_path:
        logger.info(f"Video downloaded to {file_path}")
    else:
        logger.error("Failed to download video")

    # test extract audio
    logger.info("Extracting audio")
    audio_path = video_getter.extract_audio(file_path, output_path)

    if audio_path:
        logger.info(f"Audio extracted to {audio_path}")
    else:
        logger.error("Failed to extract audio")

    # test transcribe audio
    logger.info("Transcribing audio")
    transcript = huggingface.transcribe(audio_path)

    if transcript:
        logger.info(f"Transcript: {transcript[:500]}[...]")
    else:
        logger.error("Failed to transcribe audio")
    
    # test scrape
    data = scraper.scrape(url)

    if data:
        logger.info(f"Scraped data: {data}")
    else:
        logger.error("Failed to scrape")
    
    return file_path
