from django.shortcuts import render
from ..core.post import get_all_posts, get_post_by_slug


def blog_list(request):
    posts = get_all_posts()
    return render(request, "blog_list.html", {"posts": posts})


def blog_detail(request, slug):
    post = get_post_by_slug(slug)
    return render(request, "blog_detail.html", {"post": post})
