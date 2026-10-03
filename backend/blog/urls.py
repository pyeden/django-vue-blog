from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import ArticleColumnListView, ArticleViewSet, TagListView

router = SimpleRouter()
router.register("articles", ArticleViewSet, basename="article")

urlpatterns = [
    path("columns/", ArticleColumnListView.as_view(), name="column-list"),
    path("tags/", TagListView.as_view(), name="tag-list"),
] + router.urls
