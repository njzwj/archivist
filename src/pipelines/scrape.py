import os
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests

from src.core.pipeline import Pipeline


ua = UserAgent()


def scrape(inputs: dict, **kwargs) -> dict:
    url = inputs.get("url")

    page = requests.get(url, headers={"User-Agent": ua.random()})
    if page.status_code != 200:
        raise ValueError(f"Failed to fetch page: {url}")

    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.title.string
    