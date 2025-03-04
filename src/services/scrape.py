from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import html2text
import logging
import requests
import json

from src.services import GptService


class ScrapeService:

    ua = UserAgent()
    
    def __init__(self, gpt: GptService, logger: logging.Logger):
        self.gpt = gpt
        self.logger = logger
        self.text_maker = html2text.HTML2Text()
        self.text_maker.ignore_links = True
        self.text_maker.ignore_images = True
        self.text_maker.ignore_emphasis = True
        self.text_maker.ignore_tables = True
        self.text_maker.ignore_anchors = True

    def scrape(self, url: str) -> str:
        page = requests.get(url, headers={'User-Agent': self.ua.random})
        if page.status_code != 200:
            self.logger.error(f"Failed to scrape from {url}. Status code: {page.status_code}")
            return ""

        soup = BeautifulSoup(page.content, 'html.parser')
        title = soup.title.string
        meta_tags = soup.find_all('meta')
        meta_data = {}
        for tag in meta_tags:
            if tag.get("name"):
                meta_data[tag.get("name")] = tag.get("content")
            elif tag.get("property"):
                meta_data[tag.get("property")] = tag.get("content")
            elif tag.get("itemprop"):
                meta_data[tag.get("itemprop")] = tag.get("content")
        content = self.text_maker.handle(page.content.decode('utf-8'))

        return f"Page Title: {title}\n\nMeta Data: {json.dumps(meta_data,ensure_ascii=False)}\n\nContent: {content}"
