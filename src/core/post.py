import os
import markdown
from datetime import datetime
import json

from ..utils.config import get_config

config = get_config()
post_path = config.archivist_results_path


def parse_post(obj: dict) -> dict:
    post = dict(
        meta=dict(
            source=obj["url"],
            title=obj["title"],
            slug=obj["title"],
            created_at=datetime.strptime(obj["created_at"], "%Y-%m-%d %H:%M:%S %z"),
            published_at=datetime.strptime(obj["published_at"], "%Y-%m-%d %H:%M:%S"),
            author=obj.get("author", "Unknown"),
            tags=obj.get("tags", []),
            transcript=markdown.markdown(obj.get("transcript", ""), tab_length=2),
            briefing=markdown.markdown(obj.get("briefing", ""), tab_length=2),
        ),
        content=markdown.markdown(obj.get("briefing", ""), tab_length=2),
    )
    return post


def get_all_posts(path: str = post_path) -> tuple:
    posts = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            with open(os.path.join(path, file), "r") as f:
                obj = json.load(f)
                post = parse_post(obj)
                posts.append(post)

    posts.sort(key=lambda x: x["meta"]["created_at"], reverse=True)

    tags = list(set(tag for post in posts for tag in post["meta"]["tags"]))

    return posts, tags


def get_post_by_slug(slug: str, path: str = post_path) -> dict:
    for file in os.listdir(path):
        if not file.endswith(".json"):
            continue
        if file.startswith(slug):
            with open(os.path.join(path, file), "r") as f:
                obj = json.load(f)
                post = parse_post(obj)
                return post
