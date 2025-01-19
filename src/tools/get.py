import argparse
import dotenv
import os

from ..pipelines import transcript

dotenv.load_dotenv()

power_llm_results_path = os.path.expanduser(os.getenv('POWER_LLM_RESULTS_PATH'))

video_sites = [
    'youtube',
    'bilibili',
    'vimeo',
]

def parse_args():
    parser = argparse.ArgumentParser(description="Download files from a URL to a specified output directory.")
    parser.add_argument('url', type=str, help='The URL to download the file from')
    parser.add_argument('output_dir', type=str, help='The directory to save the downloaded file', nargs='?', default=power_llm_results_path)
    return parser.parse_args()

def clean_url(url):
    """
    Clean the URL to remove unnecessary parameters.
    Args:
        url (str): The URL to clean.
    Returns:
        str: The cleaned URL.
    """
    return url.split('?')[0].strip('/\\').strip('/')

def get_wrapper(url, output_dir):
    url = clean_url(url)
    for site in video_sites:
        if site in url:
            return transcript(url, output_dir)
    raise ValueError(f"Unsupported site: {url}")

def get():
    args = parse_args()
    get_wrapper(args.url, args.output_dir)
