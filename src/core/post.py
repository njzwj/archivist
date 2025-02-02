import os
import markdown
from typing import List
from datetime import datetime
import json

from ..utils.config import get_config

config = get_config()
post_path = config.power_llm_results_path


def parse_post(obj: dict) -> dict:
    post = dict(
        meta=dict(
            source=obj["url"],
            title=obj["title"],
            slug=obj["title"],
            created_at=datetime.strptime(obj["created_at"], "%Y-%m-%d %H:%M:%S %z"),
            tags=obj.get("tags", []),
            transcript=markdown.markdown(obj.get("transcript", "")),
            briefing=markdown.markdown(obj.get("briefing", "")),
        ),
        content=markdown.markdown(obj.get("briefing", "")),
    )
    return post


def get_all_posts(path: str = post_path) -> List[dict]:
    posts = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            with open(os.path.join(path, file), "r") as f:
                obj = json.load(f)
                post = parse_post(obj)
                posts.append(post)

    posts.sort(key=lambda x: x["meta"]["created_at"], reverse=True)

    return posts


def get_post_by_slug(slug: str, path: str = post_path) -> dict:
    post_filename = os.path.join(path, f"{slug}.json")
    with open(post_filename, "r") as f:
        obj = json.load(f)
        post = parse_post(obj)
    return post
