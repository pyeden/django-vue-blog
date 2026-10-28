from django.db.models import Count, F, Q
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response
from taggit.models import Tag

from .models import Article, ArticleColumn, ArticleLike
from .serializers import (
    ArticleColumnSerializer,
    ArticleSerializer,
    TagsField,
)
from .utils import extract_toc  # noqa: F401  (kept importable for consumers)


class IsAuthorOrStaff(permissions.BasePermission):
    message = "只有作者本人或管理员可以执行此操作。"

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        return request.user.is_staff or obj.author_id == request.user.id


class ArticleViewSet(viewsets.ModelViewSet):
    serializer_class = ArticleSerializer
    lookup_field = "slug"
    lookup_value_regex = r"[^/.]+"
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsAuthorOrStaff]
    search_fields = ["title", "body"]
    ordering_fields = ["created", "updated", "total_views", "likes", "title"]
    ordering = ["-created"]

    def get_queryset(self):
        queryset = (
            Article.objects.select_related("author", "author__profile", "column")
            .prefetch_related("tags")
            .annotate(comment_count=Count("comments", filter=Q(comments__active=True)))
        )
        column = self.request.query_params.get("column")
        if column:
            column_query = Q(column__slug=column)
            if str(column).isdigit():
                column_query |= Q(column__id=int(column))
            queryset = queryset.filter(column_query)
        tag = self.request.query_params.get("tag")
        if tag:
            queryset = queryset.filter(
                Q(tags__name__iexact=tag) | Q(tags__slug__iexact=tag)
            ).distinct()
        return queryset

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        Article.objects.filter(pk=instance.pk).update(total_views=F("total_views") + 1)
        instance.total_views += 1
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, slug=None):
        article = self.get_object()
        like, created = ArticleLike.objects.get_or_create(
            article=article, user=request.user
        )
        if created:
            Article.objects.filter(pk=article.pk).update(likes=F("likes") + 1)
            liked = True
        else:
            like.delete()
            Article.objects.filter(pk=article.pk, likes__gt=0).update(likes=F("likes") - 1)
            liked = False
        article.refresh_from_db(fields=["likes"])
        return Response({"liked": liked, "likes": article.likes})

    @action(
        detail=True,
        methods=["post"],
        url_path="cover",
        parser_classes=[MultiPartParser, FormParser],
        permission_classes=[permissions.IsAuthenticatedOrReadOnly, IsAuthorOrStaff],
    )
    def cover(self, request, slug=None):
        article = self.get_object()
        self.check_object_permissions(request, article)
        file = request.FILES.get("cover")
        if file is None:
            return Response({"detail": "缺少 cover 文件。"}, status=status.HTTP_400_BAD_REQUEST)
        article.cover = file
        article.save(update_fields=["cover"])
        return Response(self.get_serializer(article).data)

    @action(detail=False, methods=["get"], url_path="hot")
    def hot(self, request):
        articles = self.get_queryset().order_by("-total_views")[:5]
        serializer = self.get_serializer(articles, many=True)
        return Response(serializer.data)


class ArticleColumnListView(ListAPIView):
    serializer_class = ArticleColumnSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return ArticleColumn.objects.annotate(
            article_count=Count("articles")
        ).order_by("title")


class TagListView(ListAPIView):
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        return Tag.objects.all().order_by("name")

    def list(self, request, *args, **kwargs):
        data = [
            {"name": tag.name, "slug": tag.slug}
            for tag in self.get_queryset()
        ]
        return Response(data)
