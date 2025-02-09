import argparse
import re
import time
import os

from ..core.item_model import ItemModel
from ..pipelines import orchestrator

from ..utils.config import get_config
from ..utils.decorators import timer, count_tokens

config = get_config()

video_sites = [
    "youtube",
    "bilibili",
    "vimeo",
]


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
        default=config.archivist_results_path,
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
    
    inputs = {
        "url": url,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
    }

    inputs = orchestrator.process("scrape", inputs)
    inputs = orchestrator.process("transcript", inputs)
    inputs = orchestrator.process("tag", inputs)
    inputs = orchestrator.process("briefing", inputs)
    
    output_dir = output_dir or config.archivist_results_path
    item = ItemModel(inputs, os.path.join(output_dir, inputs["title"] + ".json"))
    item.save()


def get():
    args = parse_args()
    get_wrapper(args.url, args.output_dir)
