from django.shortcuts import render
from ..core.post import get_all_posts, get_post_by_slug


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
