import os
import markdown
from typing import List
from datetime import datetime
import json


def parse_post(obj: dict) -> dict:
    post = dict(
        source=obj["url"],
        title=obj["title"],
        created_at=datetime.strptime(obj["created_at"], "%Y-%m-%d %H:%M:%S %z"),
        tags=obj.get("tags", []),
        transcript=markdown.markdown(obj.get("transcript", "")),
        briefing=markdown(obj.get("briefing", "")),
    )
    return post


def get_all_posts(path: str) -> List[dict]:
    posts = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            with open(os.path.join(path, file), "r") as f:
                obj = json.load(f)
                post = parse_post(obj)
                posts.append(post)

    posts.sort(key=lambda x: x["created_at"], reverse=True)

    return posts
