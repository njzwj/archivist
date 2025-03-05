from django.shortcuts import render
from datetime import datetime
import markdown
import os
import json

from src.container import Container


def count(lst) -> dict:
    cnt = {item: lst.count(item) for item in lst}
    cnt = [{"key": k, "count": v} for k, v in cnt.items() if k != ""]
    cnt.sort(key=lambda x: x["count"], reverse=True)
    return cnt


def parse_post(obj: dict) -> dict:
    transcript = obj.get("transcript", "")

    post = dict(
        meta=dict(
            source=obj["url"],
            title=obj["title"],
            slug=obj["slug"],
            created_at=datetime.strptime(obj["created_at"], "%Y-%m-%d %H:%M:%S %z"),
            published_at=datetime.strptime(obj["published_at"], "%Y-%m-%d %H:%M:%S"),
            author=obj.get("author", "Unknown"),
            tags=obj.get("tags", []),
            transcript=markdown.markdown(
                transcript if transcript else "", tab_length=2
            ),
            briefing=markdown.markdown(obj.get("briefing", ""), tab_length=2),
        ),
        content=markdown.markdown(obj.get("briefing", ""), tab_length=2),
    )
    return post


def get_all_posts():
    container = Container()
    path = os.path.expanduser(container.config()["Archivist"]["workspace"])

    posts = []
    for file in os.listdir(path):
        if file.endswith(".json"):
            with open(os.path.join(path, file), "r") as f:
                obj = json.load(f)
                obj["slug"] = file
                post = parse_post(obj)
                posts.append(post)

    posts.sort(key=lambda x: x["meta"]["created_at"], reverse=True)

    tags = [tag for post in posts for tag in post["meta"]["tags"]]
    tags = count(tags)
    authors = [post["meta"]["author"] for post in posts]
    authors = count(authors)

    return posts, tags, authors


def get_post_by_slug(slug: str) -> dict:
    container = Container()
    path = os.path.expanduser(container.config()["Archivist"]["workspace"])

    with open(os.path.join(path, slug), "r") as f:
        obj = json.load(f)
        obj["slug"] = slug
        post = parse_post(obj)
        return post


def post_list(request):
    posts, tags, authors = get_all_posts()
    return render(
        request,
        "post_list.html",
        {
            "posts": posts,
            "tags": tags,
            "authors": authors,
            "page_title": " | All Posts",
        },
    )


def post_list_tag(request, tag):
    posts, tags, authors = get_all_posts()
    posts = [post for post in posts if tag in post["meta"]["tags"]]
    return render(
        request,
        "post_list.html",
        {
            "posts": posts,
            "tags": tags,
            "authors": authors,
            "page_title": f" | tag={tag}",
        },
    )


def post_list_author(request, author):
    posts, tags, authors = get_all_posts()
    posts = [post for post in posts if author == post["meta"]["author"]]
    return render(
        request,
        "post_list.html",
        {
            "posts": posts,
            "tags": tags,
            "authors": authors,
            "page_title": f" | author={author}",
        },
    )


def post(request, slug):
    post = get_post_by_slug(slug)
    return render(request, "post.html", {"post": post})
