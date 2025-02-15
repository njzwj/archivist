import argparse
import re
import time
import os
from typing import List

from ..core.item_model import ItemModel
from ..pipelines import orchestrator

from ..utils import get_config, get_cache
from ..utils.decorators import timer, count_tokens

config = get_config()
cache = get_cache()

video_sites = [
    "youtube",
    "bilibili",
    "vimeo",
]


def parse_arguments(args: List[str]) -> dict:
    cached_args = cache.read("kwargs")
    args = dict(arg.split("=", 1) for arg in args)
    if len(args) == 0:
        args = cached_args or {}
        print(f"Using cached arguments:\n{args}")
    cache.write("kwargs", args)
    return args


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download files from a URL to a specified output directory."
    )
    parser.add_argument("url", type=str, help="The URL to download the file from")
    parser.add_argument(
        "-o",
        "--output-dir",
        type=str,
        help="The directory to save the downloaded file",
        default=config.archivist_results_path,
    )
    parser.add_argument(
        "kwargs",
        nargs=argparse.REMAINDER,
        help="Additional arguments to pass to the download function",
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
def get_wrapper(url, output_dir, kwargs):
    if re.search(r"bilibili", url):
        url = clean_url(url)

    inputs = {
        "url": url,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S %z"),
    }

    inputs = orchestrator.process("scrape", inputs, **kwargs)
    inputs = orchestrator.process("transcript", inputs, **kwargs)
    inputs = orchestrator.process("tag", inputs, **kwargs)
    inputs = orchestrator.process("brief", inputs, **kwargs)

    output_dir = output_dir or config.archivist_results_path
    item = ItemModel(inputs, os.path.join(output_dir, inputs["title"] + ".json"))
    item.save()


def get():
    args = parse_args()
    kwargs = parse_arguments(args.kwargs)
    get_wrapper(args.url, args.output_dir, kwargs)
