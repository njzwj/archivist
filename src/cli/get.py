from langchain_core.runnables import RunnablePassthrough
from operator import itemgetter
from src.runnables.tools import (
    get_video,
    extract_audio,
    transcript,
    extract_title_from_path,
    created_at,
    clean_temp_files,
    write_to_file,
)
import argparse
import re

from ..utils.config import get_config
from ..utils.decorators import timer, count_tokens

config = get_config()

video_sites = [
    "youtube",
    "bilibili",
    "vimeo",
]

chain = (
    RunnablePassthrough.assign(
        video_path=lambda inputs: get_video(inputs["url"], inputs["output_dir"]),
    )
    | RunnablePassthrough.assign(
        audio_path=lambda inputs: extract_audio(inputs["video_path"]),
    )
    | RunnablePassthrough.assign(
        transcript=lambda inputs: transcript(inputs["audio_path"]),
    )
    | RunnablePassthrough.assign(
        title=clean_temp_files,
    )
    | RunnablePassthrough.assign(
        title=lambda inputs: extract_title_from_path(inputs["video_path"]),
    )
    | {
        "output_dir": itemgetter("output_dir"),
        "url": itemgetter("url"),
        "created_at": created_at,
        "title": itemgetter("title"),
        "transcript": itemgetter("transcript"),
    }
    | write_to_file
)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download files from a URL to a specified output directory."
    )
    parser.add_argument("url", type=str, help="The URL to download the file from")
    parser.add_argument(
        "output_dir",
        type=str,
        help="The directory to save the downloaded file",
        nargs="?",
        default=config.power_llm_results_path,
    )
    return parser.parse_args()


def clean_url(url):
    """
    Clean the URL to remove unnecessary parameters.
    Args:
        url (str): The URL to clean.
    Returns:
        str: The cleaned URL.
    """
    return url.split("?")[0].strip("/\\").strip("/")


@timer()
@count_tokens()
def get_wrapper(url, output_dir):
    if re.search(r"bilibili", url):
        url = clean_url(url)
    for site in video_sites:
        if site in url:
            return chain.invoke(
                {
                    "url": url,
                    "output_dir": output_dir,
                }
            )
    raise ValueError(f"Unsupported site: {url}")


def get():
    args = parse_args()
    get_wrapper(args.url, args.output_dir)
