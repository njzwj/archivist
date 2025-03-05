from django.urls import path
from .views import post, post_list, post_list_tag, post_list_author

urlpatterns = [
    path("", post_list, name="all_posts"),
    path("tag/<str:tag>/", post_list_tag, name="posts_by_tag"),
    path("author/<str:author>/", post_list_author, name="posts_by_author"),
    path("post/<str:slug>/", post, name="post"),
]
