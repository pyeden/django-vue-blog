from django.db.models import Q
from rest_framework import serializers

from .models import Article, ArticleColumn
from .utils import extract_toc, make_excerpt


class AuthorSerializer(serializers.Serializer):
    username = serializers.CharField()
    avatar = serializers.SerializerMethodField()

    def get_avatar(self, obj):
        profile = getattr(obj, "profile", None)
        if not profile or not profile.avatar:
            return None
        request = self.context.get("request")
        url = profile.avatar.url
        return request.build_absolute_uri(url) if request else url


class TagsField(serializers.Field):
    def to_representation(self, value):
        return [tag.name for tag in value.all()]

    def to_internal_value(self, data):
        if data is None:
            return []
        if not isinstance(data, (list, tuple)):
            raise serializers.ValidationError("tags 必须是字符串数组。")
        cleaned = []
        for item in data:
            name = str(item).strip()
            if name and name not in cleaned:
                cleaned.append(name)
        return cleaned


class ColumnField(serializers.Field):
    """Read as {title, slug}; accept a slug or numeric id on write."""

    def to_representation(self, value):
        if value is None:
            return None
        return {"title": value.title, "slug": value.slug}

    def to_internal_value(self, data):
        if data in (None, "", 0):
            return None
        query = Q(slug=str(data))
        if str(data).isdigit():
            query |= Q(pk=int(data))
        column = ArticleColumn.objects.filter(query).first()
        if column is None:
            raise serializers.ValidationError("栏目不存在。")
        return column


class ArticleSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(read_only=True)
    column = ColumnField(required=False, allow_null=True)
    tags = TagsField(required=False)
    cover = serializers.ImageField(required=False, allow_null=True)
    excerpt = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()
    body_html = serializers.CharField(read_only=True)
    toc = serializers.SerializerMethodField()
    liked = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            "id", "title", "slug", "body", "body_html", "excerpt", "cover",
            "author", "column", "tags", "toc", "liked",
            "total_views", "likes", "comment_count", "created", "updated",
        ]
        read_only_fields = ["id", "slug", "total_views", "likes", "created", "updated"]
        extra_kwargs = {"body": {"required": True}}

    def get_excerpt(self, obj):
        return make_excerpt(obj.body)

    def get_comment_count(self, obj):
        annotated = getattr(obj, "comment_count", None)
        if annotated is not None:
            return annotated
        return obj.comments.filter(active=True).count()

    def get_toc(self, obj):
        return extract_toc(obj.body)

    def get_liked(self, obj):
        request = self.context.get("request")
        if not request or not request.user.is_authenticated:
            return False
        return obj.article_likes.filter(user=request.user).exists()

    def create(self, validated_data):
        tags = validated_data.pop("tags", [])
        request = self.context["request"]
        article = Article.objects.create(author=request.user, **validated_data)
        article.tags.set(tags)
        return article

    def update(self, instance, validated_data):
        tags = validated_data.pop("tags", None)
        for key, value in validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if tags is not None:
            instance.tags.set(tags)
        return instance


class ArticleColumnSerializer(serializers.ModelSerializer):
    article_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = ArticleColumn
        fields = ["id", "title", "slug", "article_count", "created"]
