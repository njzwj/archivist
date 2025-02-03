from django.shortcuts import render
from ..core.post import get_all_posts, get_post_by_slug


def post_list(request):
    posts, tags = get_all_posts()
    return render(request, "post_list.html", {"posts": posts, "tags": tags, "page_title": " | All Posts"})


def post_list_tag(request, tag):
    posts, tags = get_all_posts()
    posts = [post for post in posts if tag in post["meta"]["tags"]]
    return render(request, "post_list.html", {"posts": posts, "tags": tags, "page_title": f" | tag={tag}"})


def post(request, slug):
    post = get_post_by_slug(slug)
    return render(request, "post.html", {"post": post})
