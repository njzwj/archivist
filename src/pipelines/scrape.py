from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from langchain_core.prompts import PromptTemplate
import html2text
import json
import requests

from src.core.models import get_chat_model
from src.core.pipeline import Pipeline

ua = UserAgent()
text_maker = html2text.HTML2Text()
text_maker.ignore_links = True
text_maker.ignore_images = True
text_maker.ignore_emphasis = True
text_maker.ignore_tables = True
text_maker.ignore_anchors = True


def c(inputs):
    return inputs.content


def get_extract_keys_chain():
    model = get_chat_model()

    extract_keys_chain = (
        PromptTemplate.from_template(
            """Here is a web-scrapped content. Please extract the keys from the content.
            content:
            ```
            {content}
            ```
            Extract the following keys:
            - published_at (the published date time, e.g., 2022-01-31 18:23:45)
            - author
            Ouput format:
            ```json
            {{"published_at": "2021-01-01","author": "John Doe"}}
            ```
            But replace the values with the actual values from the content.
            The original content may not contain exactly the same name for the keys. Decide the best value to use for each key.
            If the key is not found, leave it empty.
            Do not include any other keys.
            """
        )
        | model
        | c
    )
    return extract_keys_chain


def extract_header_metadata(soup: BeautifulSoup) -> dict:
    meta_tags = soup.find_all("meta")
    meta_data = {}
    for tag in meta_tags:
        if tag.get("name"):
            meta_data[tag.get("name")] = tag.get("content")
        elif tag.get("property"):
            meta_data[tag.get("property")] = tag.get("content")
        elif tag.get("itemprop"):
            meta_data[tag.get("itemprop")] = tag.get("content")
    return meta_data


def extract_keys(obj: dict) -> dict:
    content = json.dumps(obj, ensure_ascii=False)
    extract_keys_chain = get_extract_keys_chain()
    keys = extract_keys_chain.invoke({"content": content})
    keys = keys.replace("```json", "").replace("```", "").strip()
    return json.loads(keys)


def scrape(inputs: dict, **kwargs) -> dict:
    if "title" in inputs.keys() or "content" in inputs.keys():
        return inputs

    url = inputs.get("url")

    page = requests.get(url, headers={"User-Agent": ua.random})
    if page.status_code != 200:
        raise ValueError(f"Failed to fetch page: {url}")

    soup = BeautifulSoup(page.content, "html.parser")
    title = soup.title.string
    meta_data = extract_header_metadata(soup)
    content = text_maker.handle(page.content.decode())
    keys = extract_keys({**meta_data, "content": content})

    return {**inputs, "title": title, **keys, "content": content}


description_string = """Scrape the content from the provided URL and save it under the "content" key.
With other metadata extracted from the page, such as the title, published_at, and author.
"""

scrape_pipeline = Pipeline(
    name="scrape",
    input_keys=["url"],
    output_keys=["title", "content", "published_at", "author"],
    description=description_string,
    process=scrape,
)
