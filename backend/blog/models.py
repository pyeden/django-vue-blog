from django.contrib.auth.models import User
from django.db import models
from django.utils.text import slugify
from taggit.managers import TaggableManager

from .utils import render_markdown


class ArticleColumn(models.Model):
    title = models.CharField(max_length=100)
    slug = models.SlugField(max_length=120, unique=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["title"]

    def __str__(self) -> str:
        return self.title


class Article(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles")
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    body = models.TextField()
    body_html = models.TextField(blank=True, default="")
    cover = models.ImageField(upload_to="covers/", blank=True, null=True)
    column = models.ForeignKey(
        ArticleColumn,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="articles",
    )
    tags = TaggableManager(blank=True)
    total_views = models.PositiveIntegerField(default=0)
    likes = models.PositiveIntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created"]

    def __str__(self) -> str:
        return self.title

    def _unique_slug(self) -> str:
        base = slugify(self.title, allow_unicode=True)[:200] or "article"
        candidate = base
        index = 2
        while Article.objects.filter(slug=candidate).exclude(pk=self.pk).exists():
            candidate = f"{base}-{index}"
            index += 1
        return candidate

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        self.body_html = render_markdown(self.body)
        super().save(*args, **kwargs)


class ArticleLike(models.Model):
    article = models.ForeignKey(
        Article, on_delete=models.CASCADE, related_name="article_likes"
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="article_likes")
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["article", "user"], name="unique_article_like"
            )
        ]

    def __str__(self) -> str:
        return f"{self.user} likes {self.article}"
