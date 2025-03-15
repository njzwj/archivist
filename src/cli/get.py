import os
import json
import time

from src.container import Container

container = Container()
logger = container.logger("get")


def clean_url(url):
    return url.split("?")[0].strip("/\\").strip("/")


def clean_file_name(name):
    return name.replace(":", "_").replace("/", "_").replace("\\", "_").replace("?", "_")


def scrape_page(url):
    scraper = container.scrape_service()
    content = scraper.scrape(url)
    if content:
        logger.debug(f"Scraped page content: {content[:100]}")
    else:
        logger.error("Failed to scrape")
    return content


def get_video_transcript(url):
    video_getter = container.video_getter_service()
    huggingface = container.huggingface_service()
    output_path = os.path.expanduser(container.config()["Archivist"]["workspace"])

    video_path = video_getter.download_video(url, output_path)
    if video_path:
        logger.debug(f"Video downloaded to {video_path}")
    else:
        logger.warning("Failed to download video")
        return None

    audio_path = video_getter.extract_audio(video_path, output_path)
    if audio_path:
        logger.debug(f"Audio extracted to {audio_path}")
    else:
        logger.warning("Failed to extract audio")
        os.remove(video_path)
        return None

    transcript = huggingface.transcribe(audio_path)
    if transcript:
        logger.debug(f"Transcript: {transcript[:500]}[...]")
    else:
        logger.warning("Failed to transcribe audio")
        os.remove(video_path)
        os.remove(audio_path)
        return None

    os.remove(video_path)
    os.remove(audio_path)
    return transcript


def get(url):
    extractor = container.extractor_service()

    output_path = os.path.expanduser(container.config()["Archivist"]["workspace"])
    if not os.path.exists(output_path):
        logger.info(f"Creating output directory: {output_path}")
        os.makedirs(output_path)

    url = clean_url(url)

    page_content = scrape_page(url)
    if not page_content:
        return

    metadata = extractor.extract_metadata(page_content)
    if "title" not in metadata:
        logger.error(f"Failed to extract title from page: {url}")
        return

    transcript = get_video_transcript(url)

    tags = extractor.extract_tags(
        f"Transcript:\n\n{transcript}\n\nPage content:\n\n{page_content}"
    )
    logger.debug(f"Extracted tags: {tags}")

    rewritten_content = extractor.rewrite_content(
        f"Transcript:\n\n{transcript}\n\nPage content:\n\n{page_content}"
    )
    logger.debug(f"Rewritten content: {rewritten_content[:100]}")

    data = {
        **metadata,
        "url": url,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
        "page_content": page_content,
        "transcript": transcript,
        "tags": tags,
        "briefing": rewritten_content,
    }

    cleaned_file_name = clean_file_name(metadata["title"])

    with open(f"{output_path}/{cleaned_file_name}.json", "w") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    logger.info(f"Data saved to {output_path}/{cleaned_file_name}.json")
