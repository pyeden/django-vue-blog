from django.urls import path

from .views import ArticleCommentsView, CommentDetailView

urlpatterns = [
    path("articles/<str:slug>/comments/", ArticleCommentsView.as_view(), name="article-comments"),
    path("comments/<int:pk>/", CommentDetailView.as_view(), name="comment-detail"),
]
