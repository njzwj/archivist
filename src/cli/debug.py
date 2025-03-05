import os
import json

from src.container import Container


def debug(url):
    container = Container()

    output_path = os.path.expanduser("~/Downloads")

    logger = container.logger("debug")
    video_getter = container.video_getter_service()
    scraper = container.scrape_service()
    huggingface = container.huggingface_service()
    extractor = container.extractor_service()

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
    content = scraper.scrape(url)

    if content:
        logger.info(f"Scraped page content: {content[:100]}")
    else:
        logger.error("Failed to scrape")

    # test extract
    tags = extractor.extract_tags(
        f"Transcript:\n\n{transcript}\n\nPage content:\n\n{content}"
    )
    logger.info(f"Extracted tags: {tags}")

    # metadata extract
    metadata = extractor.extract_metadata(content)
    logger.info(f"Extracted metadata: {json.dumps(metadata, ensure_ascii=False)}")

    # test rewrite
    rewritten_content = extractor.rewrite_content(
        f"Transcript:\n\n{transcript}\n\nPage content:\n\n{content}"
    )
    logger.info(f"Rewritten content: {rewritten_content}")

    return file_path
